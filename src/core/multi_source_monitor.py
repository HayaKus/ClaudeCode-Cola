"""
多源会话监控聚合器
"""
from pathlib import Path
from typing import List

from PyQt6.QtCore import QObject, pyqtSignal

from src.core.session_monitor import ClaudeSessionMonitor
from src.core.qoder_monitor import QoderSessionMonitor
from src.data.models import Session
from src.utils.logger import logger


class MultiSourceMonitor(QObject):
    """多源会话监控聚合器（支持 Claude Code 和 Qoder）"""

    sessions_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        claude_projects_dir = Path.home() / '.claude' / 'projects'
        qoder_projects_dir = Path.home() / '.qoder' / 'projects'

        self.claude_monitor = ClaudeSessionMonitor(claude_projects_dir)
        self.qoder_monitor = QoderSessionMonitor(qoder_projects_dir)

        # 连接子监控器的信号
        self.claude_monitor.sessions_updated.connect(self._on_sessions_updated)
        self.qoder_monitor.sessions_updated.connect(self._on_sessions_updated)

        logger.info("多源监控器初始化完成")

    def start(self):
        """启动所有监控器"""
        logger.info("启动多源监控器...")
        self.claude_monitor.start()
        self.qoder_monitor.start()

    def stop(self):
        """停止所有监控器"""
        logger.info("停止多源监控器")
        self.claude_monitor.stop()
        self.qoder_monitor.stop()

    def scan_all_sessions(self):
        """
        重新扫描并聚合所有来源的会话

        注意：会触发子监控器重新扫描文件系统
        """
        # 触发子监控器重新扫描
        logger.info("开始重新扫描所有来源的会话...")
        self.claude_monitor.scan_sessions()
        self.qoder_monitor.scan_sessions()

        # 聚合结果
        claude_sessions = self.claude_monitor.get_all_sessions()
        qoder_sessions = self.qoder_monitor.get_all_sessions()

        all_sessions = claude_sessions + qoder_sessions

        logger.info(f"所有会话聚合完成，共 {len(all_sessions)} 个会话 "
                   f"(Claude: {len(claude_sessions)}, Qoder: {len(qoder_sessions)})")

        self.sessions_updated.emit(all_sessions)

    def _on_sessions_updated(self, sessions: List[Session]):
        """
        子监控器会话更新时触发

        注意：这里只聚合数据，不重新扫描，避免循环触发
        """
        claude_sessions = self.claude_monitor.get_all_sessions()
        qoder_sessions = self.qoder_monitor.get_all_sessions()
        all_sessions = claude_sessions + qoder_sessions

        logger.debug(f"子监控器触发更新，聚合 {len(all_sessions)} 个会话")
        self.sessions_updated.emit(all_sessions)

    def get_all_sessions(self) -> List[Session]:
        """获取所有会话"""
        claude_sessions = self.claude_monitor.get_all_sessions()
        qoder_sessions = self.qoder_monitor.get_all_sessions()
        return claude_sessions + qoder_sessions

    def get_session(self, session_id: str) -> Session:
        """获取指定会话"""
        session = self.claude_monitor.get_session(session_id)
        if session:
            return session
        return self.qoder_monitor.get_session(session_id)
