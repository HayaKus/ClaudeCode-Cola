"""
Claude Code 会话监控器
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List

from src.core.base_monitor import BaseSessionMonitor
from src.core.todo_parser import TodoParser
from src.data.models import Session, TodoItem
from src.utils.logger import logger
from src.utils.path_decoder import decode_encoded_dirname


class ClaudeSessionMonitor(BaseSessionMonitor):
    """Claude Code 会话监控器"""

    def __init__(self, projects_dir: Path):
        super().__init__(projects_dir, source_type="claude")

    def parse_todos(self, session_id: str, file_path: Path) -> List[TodoItem]:
        """解析 Claude Code 的 todos"""
        return TodoParser.parse_claude_todos(file_path)

    def parse_session_file(self, file_path: Path) -> Session:
        """
        解析 Claude Code 会话文件

        关键逻辑：
        1. 跳过 agent- 开头的会话
        2. 跳过路径层级不足的会话
        3. 解析时间戳（ISO 8601 格式）
        4. 使用 TodoParser 解析 todos
        5. 标记 source_type 为 "claude"
        """
        session_id = file_path.stem

        # 过滤条件
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

                        # 解析时间戳（ISO 8601 格式）
                        if 'ts' in data:
                            ts = datetime.fromisoformat(data['ts'])
                            if not start_time:
                                start_time = ts
                            last_activity = ts

                        # 统计消息
                        if 'message' in data:
                            message_count += 1
                            last_message = data['message']

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

            # 提取项目名称 - 使用改进的解码方法
            try:
                relative_path = file_path.parent.relative_to(self.projects_dir)
                # 使用改进的解码方法,通过文件系统验证来正确还原路径
                project_display_name = decode_encoded_dirname(str(relative_path))
            except ValueError:
                dir_name = file_path.parent.name
                # 使用改进的解码方法
                project_display_name = decode_encoded_dirname(dir_name)

            custom_name = self.session_names.get(session_id, "")
            todos = self.parse_todos(session_id, file_path)

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
                source_type="claude"  # 关键：标记来源
            )

            return session

        except Exception as e:
            logger.error(f"读取 Claude Code 会话文件失败 {file_path}: {e}")
            return None


# 保持向后兼容
SessionMonitor = ClaudeSessionMonitor
