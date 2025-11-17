"""
系统托盘模块
"""
from typing import List
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import pyqtSignal, Qt

from src.data.models import ClaudeSession
from src.ui.tray_popup import TrayPopup
from src.utils.logger import logger


class SystemTray(QSystemTrayIcon):
    """系统托盘类"""

    # 信号
    show_window_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        # 创建默认图标
        icon = self.create_icon("🥤")
        super().__init__(icon, parent)

        # 创建弹出窗口
        self.popup = TrayPopup()
        self.popup.show_main_window.connect(self.show_window_requested)
        self.popup.open_session.connect(self.open_session)

        self.setup_menu()
        self.setup_connections()

        # 设置提示文本
        self.setToolTip("ClaudeCode-Cola 🥤")

        logger.info("系统托盘已创建")

    def setup_menu(self):
        """设置右键菜单"""
        self.menu = QMenu()
        
        # 设置菜单样式 - 模仿macOS原生样式
        self.menu.setStyleSheet("""
            QMenu {
                background-color: rgba(255, 255, 255, 0.95);
                border: 0.5px solid rgba(0, 0, 0, 0.1);
                border-radius: 6px;
                padding: 6px 0px;
            }
            QMenu::item {
                padding: 6px 20px;
                color: #000000;
                font-size: 13px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: rgba(0, 122, 255, 0.1);
                color: #000000;
            }
            QMenu::separator {
                height: 1px;
                background: rgba(0, 0, 0, 0.1);
                margin: 6px 0px;
            }
        """)

        # 显示主窗口
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show_window_requested)
        self.menu.addAction(show_action)

        self.menu.addSeparator()

        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_requested)
        self.menu.addAction(quit_action)

        # 不设置默认的contextMenu，我们手动控制
        # self.setContextMenu(menu)

    def setup_connections(self):
        """设置连接"""
        # 托盘图标激活事件
        self.activated.connect(self.on_activated)

    def on_activated(self, reason):
        """托盘图标被激活"""
        logger.debug(f"托盘图标被激活，原因: {reason}")
        
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 左键单击显示弹出窗口
            logger.info("左键单击托盘图标")
            if self.popup.isVisible():
                self.popup.hide()
            else:
                self.popup.show_at_cursor()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # 双击显示主窗口
            logger.info("双击托盘图标")
            self.show_window_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            # 右键点击时，隐藏弹出窗口并显示菜单
            logger.info("右键点击托盘图标")
            if self.popup.isVisible():
                self.popup.hide()
            # 手动显示菜单
            from PyQt6.QtGui import QCursor
            self.menu.exec(QCursor.pos())
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            logger.info("中键点击托盘图标")
            # 中键点击也显示弹出窗口
            if self.popup.isVisible():
                self.popup.hide()
            else:
                self.popup.show_at_cursor()

    def create_icon(self, emoji: str, color: QColor = None) -> QIcon:
        """
        创建托盘图标

        Args:
            emoji: 表情符号
            color: 背景颜色（不再使用，保留参数以兼容）

        Returns:
            图标对象
        """
        # 创建一个32x32的图像
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 不绘制背景，只绘制emoji
        font = painter.font()
        font.setPixelSize(28)  # 增大字体以填充空间
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)

        painter.end()

        return QIcon(pixmap)

    def update_status(self, total_count: int, need_attention_count: int):
        """
        更新托盘图标状态

        Args:
            total_count: 总会话数
            need_attention_count: 需要关注的会话数（被标记且不活跃）
        """
        # 始终使用🥤图标
        icon = self.create_icon("🥤")
        
        if need_attention_count > 0:
            tooltip = f"ClaudeCode-Cola 🥤\n🟡 {need_attention_count} 个会话需要关注"
        else:
            tooltip = f"ClaudeCode-Cola 🥤\n{total_count} 个会话"

        self.setIcon(icon)
        self.setToolTip(tooltip)

    def update_active_sessions_menu(self, sessions: List[ClaudeSession]):
        """
        更新弹出窗口

        Args:
            sessions: 会话列表
        """
        # 更新弹出窗口
        self.popup.update_sessions(sessions)

    def open_session(self, session: ClaudeSession):
        """
        打开会话所在目录

        Args:
            session: 会话对象
        """
        import subprocess
        try:
            # 在 Finder 中打开项目目录
            subprocess.run(['open', session.project_path], check=True)
            logger.info(f"打开会话目录: {session.project_path}")
        except Exception as e:
            logger.error(f"打开会话目录失败: {e}")

    def show_notification(self, title: str, message: str, notification_type: str = "info"):
        """
        显示系统通知

        Args:
            title: 通知标题
            message: 通知内容
            notification_type: 通知类型 (info/warning/error)
        """
        icon_map = {
            "info": QSystemTrayIcon.MessageIcon.Information,
            "warning": QSystemTrayIcon.MessageIcon.Warning,
            "error": QSystemTrayIcon.MessageIcon.Critical,
        }

        icon = icon_map.get(notification_type, QSystemTrayIcon.MessageIcon.Information)
        self.showMessage(title, message, icon, 3000)  # 显示3秒
        logger.info(f"显示通知: {title} - {message}")
