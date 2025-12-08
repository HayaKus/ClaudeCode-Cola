"""
基础会话监控器
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

from PyQt6.QtCore import QObject, pyqtSignal

from src.data.models import Session, TodoItem
from src.utils.logger import logger

PINNED_SESSIONS_FILE = Path.home() / '.claudecode-cola' / 'pinned_sessions.json'
SESSION_NAMES_FILE = Path.home() / '.claudecode-cola' / 'session_names.json'


class BaseSessionMonitor(QObject):
    """基础会话监控器抽象类"""

    sessions_updated = pyqtSignal(list)

    def __init__(self, projects_dir: Path, source_type: str):
        super().__init__()
        self.projects_dir = projects_dir
        self.source_type = source_type  # "claude" 或 "qoder"
        self.sessions: Dict[str, Session] = {}
        self.pinned_sessions: Set[str] = set()
        self.session_names: Dict[str, str] = {}

        logger.info(f"{source_type} 监控器初始化，监控目录: {projects_dir}")

        self.load_pinned_sessions()
        self.load_session_names()

    def start(self):
        """启动监控"""
        logger.info(f"启动 {self.source_type} 会话监控...")

        if not self.projects_dir.exists():
            logger.warning(f"项目目录不存在: {self.projects_dir}")
            self.projects_dir.mkdir(parents=True, exist_ok=True)

        self.scan_sessions()

    def stop(self):
        """停止监控"""
        logger.info(f"停止 {self.source_type} 会话监控")

    def load_pinned_sessions(self):
        """加载标记的会话列表（所有来源共用）"""
        try:
            if PINNED_SESSIONS_FILE.exists():
                with open(PINNED_SESSIONS_FILE, 'r', encoding='utf-8') as f:
                    self.pinned_sessions = set(json.load(f))
        except Exception as e:
            logger.error(f"加载标记会话配置失败: {e}")
            self.pinned_sessions = set()

    def load_session_names(self):
        """加载自定义会话名称（所有来源共用）"""
        try:
            if SESSION_NAMES_FILE.exists():
                with open(SESSION_NAMES_FILE, 'r', encoding='utf-8') as f:
                    self.session_names = json.load(f)
        except Exception as e:
            logger.error(f"加载自定义名称配置失败: {e}")
            self.session_names = {}

    def scan_sessions(self) -> List[Session]:
        """扫描所有会话"""
        jsonl_files = list(self.projects_dir.rglob("*.jsonl"))
        logger.info(f"找到 {len(jsonl_files)} 个 {self.source_type} 会话文件")

        self.sessions.clear()

        for file_path in jsonl_files:
            try:
                session = self.parse_session_file(file_path)
                if session:
                    self.sessions[session.session_id] = session
            except Exception as e:
                logger.error(f"解析 {self.source_type} 会话文件失败 {file_path}: {e}")

        sessions_list = list(self.sessions.values())
        self.sessions_updated.emit(sessions_list)

        logger.info(f"{self.source_type} 会话扫描完成，共 {len(self.sessions)} 个会话")
        return sessions_list

    def parse_session_file(self, file_path: Path) -> Session:
        """
        解析会话文件（子类必须实现）

        返回 Session 对象，如果跳过则返回 None
        """
        raise NotImplementedError("子类必须实现 parse_session_file 方法")

    def parse_todos(self, session_id: str, file_path: Path) -> List[TodoItem]:
        """
        解析 todos（子类必须实现）
        """
        raise NotImplementedError("子类必须实现 parse_todos 方法")

    def check_session_active(self, file_path: Path) -> bool:
        """
        检查会话是否活跃（通过文件修改时间判断）

        规则：文件在最近 2 分钟（120秒）内有修改才标记为活跃
        """
        try:
            file_stat = file_path.stat()
            file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
            time_diff = (datetime.now() - file_mtime).total_seconds()
            return time_diff < 120  # 2分钟
        except Exception as e:
            logger.debug(f"检查文件修改时间失败: {e}")
            return False

    def get_session(self, session_id: str) -> Session:
        """获取指定会话"""
        return self.sessions.get(session_id)

    def get_all_sessions(self) -> List[Session]:
        """获取所有会话"""
        return list(self.sessions.values())
