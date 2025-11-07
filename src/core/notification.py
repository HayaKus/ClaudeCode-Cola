"""
通知系统模块
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

from .models import Session, SessionStatus
from .config import ConfigManager
from .iterm2_integration import ITerm2Integration


class NotificationType(Enum):
    """通知类型"""
    TODO_COMPLETE = "todo_complete"
    SESSION_INACTIVE = "session_inactive"
    SESSION_CRASHED = "session_crashed"
    HIGH_RESOURCE_USAGE = "high_resource"
    MILESTONE_REACHED = "milestone"


class NotificationManager:
    """通知管理器"""

    def __init__(self, config_manager: ConfigManager):
        """初始化通知管理器"""
        self.config_manager = config_manager
        self.config = config_manager.config.notifications
        self.performance_config = config_manager.config.performance
        self.iterm2 = ITerm2Integration()
        self.last_notifications: Dict[str, datetime] = {}
        self.notification_interval = timedelta(minutes=30)  # 相同通知的最小间隔

    def check_and_notify(self, sessions: List[Session]) -> None:
        """检查会话状态并发送通知"""
        if not self.config.enabled:
            return

        for session in sessions:
            # 检查任务完成
            if self.config.todo_complete:
                self._check_todo_completion(session)

            # 检查会话闲置
            if self.config.session_inactive:
                self._check_session_inactive(session)

            # 检查会话崩溃
            if self.config.session_crashed:
                self._check_session_crashed(session)

            # 检查资源使用
            if self.config.high_resource_usage:
                self._check_resource_usage(session)

    def _check_todo_completion(self, session: Session) -> None:
        """检查任务完成情况"""
        if not session.todo_progress:
            return

        notification_key = f"todo_complete_{session.id}"

        # 检查是否100%完成
        if session.todo_progress.percentage == 100:
            if self._should_notify(notification_key):
                self.send_notification(
                    title="任务完成！",
                    message=f"会话 '{session.name}' 的所有任务已完成",
                    subtitle=f"共完成 {session.todo_progress.total} 个任务",
                    notification_type=NotificationType.TODO_COMPLETE
                )

        # 检查里程碑（50%, 75%）
        elif session.todo_progress.percentage >= 75:
            milestone_key = f"milestone_75_{session.id}"
            if self._should_notify(milestone_key, interval=timedelta(hours=2)):
                self.send_notification(
                    title="进度更新",
                    message=f"会话 '{session.name}' 已完成 75%",
                    subtitle=f"{session.todo_progress.completed}/{session.todo_progress.total} 个任务",
                    notification_type=NotificationType.MILESTONE_REACHED
                )

        elif session.todo_progress.percentage >= 50:
            milestone_key = f"milestone_50_{session.id}"
            if self._should_notify(milestone_key, interval=timedelta(hours=2)):
                self.send_notification(
                    title="进度更新",
                    message=f"会话 '{session.name}' 已完成一半",
                    subtitle=f"{session.todo_progress.completed}/{session.todo_progress.total} 个任务",
                    notification_type=NotificationType.MILESTONE_REACHED
                )

    def _check_session_inactive(self, session: Session) -> None:
        """检查会话是否长时间未活动"""
        if not session.performance:
            return

        inactive_threshold = self.performance_config.inactive_threshold_minutes
        notification_key = f"inactive_{session.id}"

        if session.performance.inactive_minutes > inactive_threshold:
            if self._should_notify(notification_key):
                self.send_notification(
                    title="会话闲置提醒",
                    message=f"会话 '{session.name}' 已闲置 {session.performance.inactive_minutes} 分钟",
                    subtitle="考虑暂停或关闭会话",
                    notification_type=NotificationType.SESSION_INACTIVE
                )

    def _check_session_crashed(self, session: Session) -> None:
        """检查会话是否崩溃"""
        notification_key = f"crashed_{session.id}"

        if session.status == SessionStatus.CRASHED:
            if self._should_notify(notification_key, interval=timedelta(minutes=5)):
                self.send_notification(
                    title="会话异常",
                    message=f"会话 '{session.name}' 已异常退出",
                    subtitle="请检查并恢复会话",
                    notification_type=NotificationType.SESSION_CRASHED
                )

    def _check_resource_usage(self, session: Session) -> None:
        """检查资源使用情况"""
        if not session.performance:
            return

        cpu_threshold = self.performance_config.high_cpu_threshold
        notification_key = f"high_cpu_{session.id}"

        if session.performance.cpu_percent > cpu_threshold:
            if self._should_notify(notification_key, interval=timedelta(minutes=10)):
                self.send_notification(
                    title="资源占用警告",
                    message=f"会话 '{session.name}' CPU 使用率过高",
                    subtitle=f"当前 CPU: {session.performance.cpu_percent:.1f}%",
                    notification_type=NotificationType.HIGH_RESOURCE_USAGE
                )

    def _should_notify(self, key: str, interval: Optional[timedelta] = None) -> bool:
        """检查是否应该发送通知（避免频繁通知）"""
        if interval is None:
            interval = self.notification_interval

        # 检查通知级别
        if self.config.level == "none":
            return False

        now = datetime.now()
        last_notification = self.last_notifications.get(key)

        if last_notification is None:
            self.last_notifications[key] = now
            return True

        if now - last_notification >= interval:
            self.last_notifications[key] = now
            return True

        return False

    def send_notification(self, title: str, message: str, subtitle: str = "",
                         notification_type: NotificationType = None) -> bool:
        """发送通知"""
        # 检查通知级别
        if self.config.level == "none":
            return False

        if self.config.level == "important":
            # 只发送重要通知
            important_types = [
                NotificationType.TODO_COMPLETE,
                NotificationType.SESSION_CRASHED,
                NotificationType.HIGH_RESOURCE_USAGE
            ]
            if notification_type not in important_types:
                return False

        # 发送通知
        return self.iterm2.send_notification(title, message, subtitle)

    def clear_notification_history(self, session_id: str) -> None:
        """清除会话的通知历史"""
        keys_to_remove = [k for k in self.last_notifications.keys() if session_id in k]
        for key in keys_to_remove:
            del self.last_notifications[key]