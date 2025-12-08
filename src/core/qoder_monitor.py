"""
Qoder 会话监控器
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List

from src.core.base_monitor import BaseSessionMonitor
from src.core.todo_parser import TodoParser
from src.data.models import Session, TodoItem
from src.utils.logger import logger


class QoderSessionMonitor(BaseSessionMonitor):
    """Qoder 会话监控器"""

    def __init__(self, projects_dir: Path):
        super().__init__(projects_dir, source_type="qoder")

    def parse_todos(self, session_id: str, file_path: Path) -> List[TodoItem]:
        """解析 Qoder 的 todos（从独立的 json 文件）"""
        return TodoParser.parse_qoder_todos(session_id)

    def parse_session_file(self, file_path: Path) -> Session:
        """
        解析 Qoder 会话文件

        关键差异：
        1. 时间戳字段为 created_at/updated_at（毫秒级 Unix 时间戳）
        2. 需要除以 1000 转换为秒级时间戳
        3. Todos 从独立文件解析
        4. 标记 source_type 为 "qoder"
        """
        session_id = file_path.stem

        # 过滤条件（与 Claude 相同）
        if session_id.startswith('agent-'):
            logger.debug(f"跳过 agent- 会话: {session_id}")
            return None

        project_path = str(file_path.parent)
        if project_path.count('/') < 2:
            logger.debug(f"跳过路径层级不足的会话: {project_path}")
            return None

        start_time = None
        last_activity = None
        message_count = 0
        last_message = ""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())

                        # 解析时间戳（毫秒级 Unix 时间戳）
                        if 'created_at' in data:
                            ts = datetime.fromtimestamp(data['created_at'] / 1000)  # 关键：除以1000
                            if not start_time:
                                start_time = ts
                            last_activity = ts

                        # 统计消息
                        if 'role' in data:
                            message_count += 1
                            last_message = str(data)

                    except json.JSONDecodeError:
                        continue

            # 默认值处理
            if not start_time:
                start_time = datetime.now()
            if not last_activity:
                last_activity = start_time

            # 检测活跃状态
            is_active = self.check_session_active(file_path)
            is_pinned = session_id in self.pinned_sessions

            # 提取项目名称
            try:
                relative_path = file_path.parent.relative_to(self.projects_dir)
                project_display_name = '/' + str(relative_path).lstrip('-').replace('-', '/')
            except ValueError:
                dir_name = file_path.parent.name
                project_display_name = '/' + dir_name.lstrip('-').replace('-', '/')

            custom_name = self.session_names.get(session_id, "")
            logger.info(f"🔍 正在解析 Qoder 会话 todos: {session_id}")
            todos = self.parse_todos(session_id, file_path)  # 从独立文件解析
            logger.info(f"📊 Qoder 会话 {session_id} 解析到 {len(todos)} 个 todos")

            session = Session(
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
                file_path=str(file_path),
                source_type="qoder"  # 关键：标记来源
            )

            return session

        except Exception as e:
            logger.error(f"读取 Qoder 会话文件失败 {file_path}: {e}")
            return None
