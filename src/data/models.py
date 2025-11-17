"""
数据模型定义
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class TodoStatus(Enum):
    """Todo状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class TodoItem:
    """TodoWrite任务项"""
    content: str
    status: TodoStatus
    active_form: str
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    @property
    def status_icon(self) -> str:
        """状态图标"""
        icons = {
            TodoStatus.COMPLETED: '✅',
            TodoStatus.IN_PROGRESS: '🔄',
            TodoStatus.PENDING: '⏳'
        }
        return icons.get(self.status, '❓')

    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == TodoStatus.COMPLETED

    def __str__(self) -> str:
        return f"{self.status_icon} {self.content}"


@dataclass
class ClaudeSession:
    """Claude Code会话"""
    session_id: str
    project_path: str
    project_name: str
    start_time: datetime
    last_activity: datetime
    is_active: bool = False
    is_pinned: bool = False
    custom_name: str = ""  # 用户自定义项目名称
    todos: List[TodoItem] = field(default_factory=list)
    message_count: int = 0
    last_message: str = ""
    file_path: str = ""

    @property
    def duration(self) -> str:
        """会话持续时间"""
        delta = datetime.now() - self.start_time
        total_seconds = delta.total_seconds()

        # 处理负数时长
        if total_seconds < 0:
            delta = datetime.now() - self.last_activity
            total_seconds = delta.total_seconds()

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    @property
    def todo_progress(self) -> str:
        """返回任务进度字符串"""
        if not self.todos:
            return "无任务"
        completed = sum(1 for t in self.todos if t.is_completed)
        total = len(self.todos)
        # 格式: [最后任务状态图标 完成数/总数] 最后任务内容
        return f"[{self.todos[-1].status_icon} {completed}/{total}] {self.todos[-1].content}"

    @property
    def progress_percentage(self) -> int:
        """进度百分比"""
        if not self.todos:
            return 0
        completed = sum(1 for t in self.todos if t.is_completed)
        total = len(self.todos)
        if total == 0:
            return 0
        return int((completed / total) * 100)

    @property
    def status_icon(self) -> str:
        """状态图标"""
        if self.is_pinned and self.is_active:
            return "📌🟢"
        elif self.is_pinned and not self.is_active:
            return "📌🟡"
        elif self.is_active:
            return "🟢"
        else:
            return "🟡"

    @property
    def status_color(self) -> str:
        """状态颜色"""
        if not self.is_active:
            return "warning"  # 黄色
        return "success"      # 绿色

    def __str__(self) -> str:
        if not self.todos:
            return f"{self.status_icon} {self.project_name}"
        completed = sum(1 for t in self.todos if t.is_completed)
        total = len(self.todos)
        return f"{self.status_icon} {self.project_name} ({completed}/{total})"
