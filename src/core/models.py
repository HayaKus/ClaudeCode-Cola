"""
数据模型定义
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class SessionStatus(Enum):
    """会话状态"""
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    CRASHED = "crashed"


class TodoStatus(Enum):
    """Todo 任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class TodoItem:
    """Todo 项"""
    content: str
    status: TodoStatus
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class ProcessInfo:
    """进程信息"""
    pid: int
    iTerm_window_id: str
    iTerm_window_title: str


@dataclass
class PerformanceInfo:
    """性能信息"""
    cpu_percent: float
    memory_mb: float
    inactive_minutes: int


@dataclass
class TodoProgress:
    """Todo 进度"""
    total: int
    completed: int
    current_task: Optional[str]
    last_completed_at: Optional[datetime]
    items: List[TodoItem] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        """计算完成百分比"""
        if self.total == 0:
            return 0.0
        return (self.completed / self.total) * 100


@dataclass
class Session:
    """会话信息"""
    id: str
    name: str
    work_dir: str
    created_at: datetime
    last_active: datetime
    is_starred: bool = False
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    process_info: Optional[ProcessInfo] = None
    performance: Optional[PerformanceInfo] = None
    todo_progress: Optional[TodoProgress] = None
    status: SessionStatus = SessionStatus.RUNNING
    closed_at: Optional[datetime] = None
    closed_reason: Optional[str] = None
    duration: Optional[str] = None

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "work_dir": self.work_dir,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "is_starred": self.is_starred,
            "tags": self.tags,
            "notes": self.notes,
            "status": self.status.value,
            "process_info": {
                "pid": self.process_info.pid,
                "iTerm_window_id": self.process_info.iTerm_window_id,
                "iTerm_window_title": self.process_info.iTerm_window_title
            } if self.process_info else None,
            "performance": {
                "cpu_percent": self.performance.cpu_percent,
                "memory_mb": self.performance.memory_mb,
                "inactive_minutes": self.performance.inactive_minutes
            } if self.performance else None,
            "todo_progress": {
                "total": self.todo_progress.total,
                "completed": self.todo_progress.completed,
                "current_task": self.todo_progress.current_task,
                "last_completed_at": self.todo_progress.last_completed_at.isoformat() if self.todo_progress.last_completed_at else None,
                "items": [
                    {
                        "content": item.content,
                        "status": item.status.value,
                        "created_at": item.created_at.isoformat(),
                        "completed_at": item.completed_at.isoformat() if item.completed_at else None
                    }
                    for item in self.todo_progress.items
                ]
            } if self.todo_progress else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "closed_reason": self.closed_reason,
            "duration": self.duration
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Session':
        """从字典创建"""
        # 处理日期时间
        created_at = datetime.fromisoformat(data["created_at"])
        last_active = datetime.fromisoformat(data["last_active"])
        closed_at = datetime.fromisoformat(data["closed_at"]) if data.get("closed_at") else None

        # 处理进程信息
        process_info = None
        if data.get("process_info"):
            pi = data["process_info"]
            process_info = ProcessInfo(
                pid=pi["pid"],
                iTerm_window_id=pi["iTerm_window_id"],
                iTerm_window_title=pi["iTerm_window_title"]
            )

        # 处理性能信息
        performance = None
        if data.get("performance"):
            perf = data["performance"]
            performance = PerformanceInfo(
                cpu_percent=perf["cpu_percent"],
                memory_mb=perf["memory_mb"],
                inactive_minutes=perf["inactive_minutes"]
            )

        # 处理 Todo 进度
        todo_progress = None
        if data.get("todo_progress"):
            tp = data["todo_progress"]
            items = []
            for item_data in tp.get("items", []):
                item = TodoItem(
                    content=item_data["content"],
                    status=TodoStatus(item_data["status"]),
                    created_at=datetime.fromisoformat(item_data["created_at"]),
                    completed_at=datetime.fromisoformat(item_data["completed_at"]) if item_data.get("completed_at") else None
                )
                items.append(item)

            todo_progress = TodoProgress(
                total=tp["total"],
                completed=tp["completed"],
                current_task=tp.get("current_task"),
                last_completed_at=datetime.fromisoformat(tp["last_completed_at"]) if tp.get("last_completed_at") else None,
                items=items
            )

        return cls(
            id=data["id"],
            name=data["name"],
            work_dir=data["work_dir"],
            created_at=created_at,
            last_active=last_active,
            is_starred=data.get("is_starred", False),
            tags=data.get("tags", []),
            notes=data.get("notes", ""),
            process_info=process_info,
            performance=performance,
            todo_progress=todo_progress,
            status=SessionStatus(data.get("status", SessionStatus.RUNNING.value)),
            closed_at=closed_at,
            closed_reason=data.get("closed_reason"),
            duration=data.get("duration")
        )


@dataclass
class Template:
    """会话模板"""
    id: str
    name: str
    work_dir: str
    name_pattern: str
    tags: List[str] = field(default_factory=list)
    default_todos: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "work_dir": self.work_dir,
            "name_pattern": self.name_pattern,
            "tags": self.tags,
            "default_todos": self.default_todos
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Template':
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            work_dir=data["work_dir"],
            name_pattern=data["name_pattern"],
            tags=data.get("tags", []),
            default_todos=data.get("default_todos", [])
        )