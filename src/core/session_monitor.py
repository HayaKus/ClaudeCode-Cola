"""
会话监控器模块
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import psutil
from PyQt6.QtCore import QObject, pyqtSignal

from src.data.models import ClaudeSession, TodoItem, TodoStatus
from src.utils.logger import logger

# 标记会话配置文件
PINNED_SESSIONS_FILE = Path.home() / '.claudecode-cola' / 'pinned_sessions.json'
# 自定义名称配置文件
SESSION_NAMES_FILE = Path.home() / '.claudecode-cola' / 'session_names.json'


class SessionMonitor(QObject):
    """会话监控器"""

    # 信号：会话数据更新
    sessions_updated = pyqtSignal(list)

    def __init__(self, projects_dir: Path):
        super().__init__()
        self.projects_dir = projects_dir
        self.sessions: Dict[str, ClaudeSession] = {}
        self.pinned_sessions: Set[str] = set()
        self.session_names: Dict[str, str] = {}

        logger.info(f"会话监控器初始化，监控目录: {projects_dir}")

        # 加载标记的会话列表
        self.load_pinned_sessions()
        # 加载自定义名称
        self.load_session_names()

    def start(self):
        """启动监控"""
        logger.info("启动会话监控...")

        # 确保目录存在
        if not self.projects_dir.exists():
            logger.warning(f"项目目录不存在: {self.projects_dir}")
            self.projects_dir.mkdir(parents=True, exist_ok=True)

        # 初始扫描
        self.scan_sessions()

    def stop(self):
        """停止监控"""
        logger.info("停止会话监控")

    def load_pinned_sessions(self):
        """加载标记的会话列表"""
        try:
            if PINNED_SESSIONS_FILE.exists():
                with open(PINNED_SESSIONS_FILE, 'r', encoding='utf-8') as f:
                    self.pinned_sessions = set(json.load(f))
                logger.info(f"已加载 {len(self.pinned_sessions)} 个标记的会话")
            else:
                logger.info("未找到标记会话配置文件")
        except Exception as e:
            logger.error(f"加载标记会话配置失败: {e}")
            self.pinned_sessions = set()
    
    def load_session_names(self):
        """加载自定义会话名称"""
        try:
            if SESSION_NAMES_FILE.exists():
                with open(SESSION_NAMES_FILE, 'r', encoding='utf-8') as f:
                    self.session_names = json.load(f)
                logger.info(f"已加载 {len(self.session_names)} 个自定义会话名称")
            else:
                logger.info("未找到自定义名称配置文件")
        except Exception as e:
            logger.error(f"加载自定义名称配置失败: {e}")
            self.session_names = {}

    def scan_sessions(self):
        """扫描所有会话"""
        logger.debug("扫描会话文件...")

        # 查找所有 .jsonl 文件
        jsonl_files = list(self.projects_dir.rglob("*.jsonl"))
        logger.debug(f"找到 {len(jsonl_files)} 个会话文件")

        # 清空现有会话
        self.sessions.clear()

        # 处理每个会话文件
        for file_path in jsonl_files:
            try:
                session = self.parse_session_file(file_path)
                if session:
                    self.sessions[session.session_id] = session
            except Exception as e:
                logger.error(f"解析会话文件失败 {file_path}: {e}")

        # 发送更新信号
        sessions_list = list(self.sessions.values())
        self.sessions_updated.emit(sessions_list)

        logger.info(f"会话扫描完成，共 {len(self.sessions)} 个会话")

    def parse_session_file(self, file_path: Path) -> ClaudeSession:
        """
        解析会话文件

        Args:
            file_path: 会话文件路径

        Returns:
            会话对象
        """
        session_id = file_path.stem

        # 过滤掉看起来不是真实会话的ID（如agent-开头的）
        if session_id.startswith('agent-'):
            logger.debug(f"跳过agent-会话: {session_id}")
            return None

        # 获取项目路径并检查层级
        project_path = str(file_path.parent)
        # 过滤掉不完整的路径（如只有"/"这种）
        # 至少需要包括2层路径
        if project_path.count('/') < 2:
            logger.debug(f"跳过路径层级不足的会话: {project_path}")
            return None

        todos = []
        start_time = None
        last_activity = None
        message_count = 0
        last_message = ""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())

                        # 解析时间戳
                        if 'ts' in data:
                            ts = datetime.fromisoformat(data['ts'])
                            if not start_time:
                                start_time = ts
                            last_activity = ts

                        # 解析 TodoWrite - 检查 message.content 中的 tool_use
                        if 'message' in data and 'content' in data['message']:
                            for item in data['message']['content']:
                                if isinstance(item, dict) and item.get('type') == 'tool_use' and item.get('name') == 'TodoWrite':
                                    # 找到了TodoWrite工具调用
                                    if 'input' in item and 'todos' in item['input']:
                                        todos_list = item['input']['todos']
                                        if isinstance(todos_list, list):
                                            # 清空之前的todos，使用最新的
                                            todos = []
                                            for todo_item in todos_list:
                                                try:
                                                    todo = TodoItem(
                                                        content=todo_item.get('content', ''),
                                                        status=TodoStatus(todo_item.get('status', 'pending')),
                                                        active_form=todo_item.get('activeForm', ''),
                                                    )
                                                    todos.append(todo)
                                                except Exception as e:
                                                    logger.debug(f"解析Todo项失败: {e}")

                        # 统计消息
                        if 'message' in data:
                            message_count += 1
                            last_message = data['message']

                    except json.JSONDecodeError:
                        continue

            # 创建会话对象
            if not start_time:
                start_time = datetime.now()
            if not last_activity:
                last_activity = start_time

            # 检测会话是否活跃（使用文件修改时间判断，和CLI版本保持一致）
            is_active = self.check_session_active(file_path)

            # 检查会话是否被标记
            is_pinned = session_id in self.pinned_sessions

            # 从完整路径中提取相对于 .claude/projects 的路径作为项目名
            try:
                # 获取相对于 projects 目录的路径
                relative_path = file_path.parent.relative_to(self.projects_dir)
                # Claude Code 使用"-"替代"/"，我们需要转换回来
                # 例如："-Users-haya-Code-fries" -> "/Users/haya/Code/fries"
                project_display_name = '/' + str(relative_path).lstrip('-').replace('-', '/')
            except ValueError:
                # 如果无法获取相对路径，使用目录名并转换
                dir_name = file_path.parent.name
                project_display_name = '/' + dir_name.lstrip('-').replace('-', '/')

            # 获取自定义名称
            custom_name = self.session_names.get(session_id, "")
            
            session = ClaudeSession(
                session_id=session_id,
                project_path=project_path,
                project_name=project_display_name,
                start_time=start_time,
                last_activity=last_activity,
                is_active=is_active,
                is_pinned=is_pinned,
                custom_name=custom_name,
                todos=todos,
                message_count=message_count,
                last_message=last_message,
                file_path=str(file_path)
            )

            return session

        except Exception as e:
            logger.error(f"读取会话文件失败 {file_path}: {e}")
            return None

    def check_session_active(self, file_path: Path) -> bool:
        """
        检查会话是否活跃（通过文件修改时间判断，和CLI版本保持一致）

        Args:
            file_path: 会话文件路径

        Returns:
            是否活跃
        """
        try:
            file_stat = file_path.stat()
            file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
            time_diff = (datetime.now() - file_mtime).total_seconds()
            # 只有文件在最近2分钟内有修改才标记为活跃
            if time_diff < 120:  # 2分钟
                return True
        except Exception as e:
            logger.debug(f"检查文件修改时间失败: {e}")

        return False

    def get_session(self, session_id: str) -> ClaudeSession:
        """
        获取指定会话

        Args:
            session_id: 会话ID

        Returns:
            会话对象
        """
        return self.sessions.get(session_id)

    def get_all_sessions(self) -> List[ClaudeSession]:
        """
        获取所有会话

        Returns:
            会话列表
        """
        return list(self.sessions.values())
