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
class Session:
    """AI 会话（支持 Claude Code 和 Qoder）"""
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
    source_type: str = "claude"  # 新增字段："claude" 或 "qoder"

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

        # 确定整体进度图标
        if completed == total:
            progress_icon = "✅"  # 全部完成
        elif any(t.status == TodoStatus.IN_PROGRESS for t in self.todos):
            progress_icon = "🔄"  # 有进行中的任务
        elif completed > 0:
            progress_icon = "⏳"  # 部分完成
        else:
            progress_icon = "⏳"  # 未开始

        # 找到当前最相关的任务：优先显示进行中的，其次是第一个待完成的
        current_task = None
        for todo in self.todos:
            if todo.status == TodoStatus.IN_PROGRESS:
                current_task = todo
                break

        if not current_task:
            # 没有进行中的任务，找第一个待完成的
            for todo in self.todos:
                if not todo.is_completed:
                    current_task = todo
                    break

        # 如果全部完成，显示最后一个任务
        if not current_task and self.todos:
            current_task = self.todos[-1]

        task_content = current_task.content if current_task else ""
        return f"[{progress_icon} {completed}/{total}] {task_content}"

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


# 保持向后兼容
ClaudeSession = Session
