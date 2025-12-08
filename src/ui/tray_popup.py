"""
系统托盘弹出窗口模块
"""
from typing import List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QScrollArea, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.data.models import ClaudeSession
from src.utils.logger import logger


class TrayPopup(QWidget):
    """系统托盘弹出窗口"""
    
    # 信号
    show_main_window = pyqtSignal()
    open_session = pyqtSignal(ClaudeSession)
    
    def __init__(self):
        super().__init__()
        self.sessions: List[ClaudeSession] = []
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 设置窗口属性 - 使用Popup类型，配合不激活属性避免切换桌面
        self.setWindowFlags(
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # 显示时不激活
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)  # macOS特定：总是显示工具窗口
        
        # 主容器
        container = QFrame()
        container.setObjectName("container")
        container.setStyleSheet("""
            QFrame#container {
                background: white;
                border-radius: 12px;
                border: 1px solid #E5E5EA;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        # 容器内布局
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # 标题栏
        header = self.create_header()
        layout.addWidget(header)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background: #E5E5EA;")
        line.setMaximumHeight(1)
        layout.addWidget(line)
        
        # 会话列表（可滚动）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #C7C7CC;
                border-radius: 3px;
            }
        """)
        
        self.sessions_widget = QWidget()
        self.sessions_layout = QVBoxLayout(self.sessions_widget)
        self.sessions_layout.setContentsMargins(0, 0, 0, 0)
        self.sessions_layout.setSpacing(6)
        
        scroll.setWidget(self.sessions_widget)
        layout.addWidget(scroll)
        
        # 底部按钮
        footer = self.create_footer()
        layout.addWidget(footer)
        
        # 设置固定大小
        self.setFixedSize(320, 400)
        
    def create_header(self) -> QWidget:
        """创建标题栏"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title = QLabel("🥤 ClaudeCode-Cola")
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #1F2937;
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # 统计信息
        self.stats_label = QLabel("0 个活跃会话")
        self.stats_label.setStyleSheet("""
            font-size: 11px;
            color: #6B7280;
        """)
        layout.addWidget(self.stats_label)
        
        return header
    
    def create_footer(self) -> QWidget:
        """创建底部按钮"""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 打开主窗口按钮
        open_btn = QPushButton("打开主窗口")
        open_btn.setStyleSheet("""
            QPushButton {
                background: #0066CC;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #0052A3;
            }
            QPushButton:pressed {
                background: #004080;
            }
        """)
        open_btn.clicked.connect(self.show_main_window.emit)
        layout.addWidget(open_btn)
        
        return footer
    
    def update_sessions(self, sessions: List[ClaudeSession]):
        """更新会话列表"""
        self.sessions = sessions
        
        # 清空现有会话
        while self.sessions_layout.count():
            item = self.sessions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 显示活跃会话或被标记的会话（与主窗口保持一致）
        displayed_sessions = [s for s in sessions if s.is_active or s.is_pinned]
        
        # 排序：标记的在前，最后活动时间倒序
        displayed_sessions = sorted(
            displayed_sessions,
            key=lambda s: (s.is_pinned, s.last_activity),
            reverse=True
        )[:10]  # 最多显示10个
        
        # 统计活跃会话数
        active_count = sum(1 for s in displayed_sessions if s.is_active)
        
        # 更新统计
        if active_count > 0:
            self.stats_label.setText(f"{active_count} 个活跃会话")
        else:
            self.stats_label.setText(f"{len(displayed_sessions)} 个会话")
        
        if not displayed_sessions:
            # 显示空状态
            empty = QLabel("暂无会话")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("""
                color: #9CA3AF;
                font-size: 12px;
                padding: 40px 0;
            """)
            self.sessions_layout.addWidget(empty)
        else:
            # 显示会话卡片
            for session in displayed_sessions:
                card = self.create_session_card(session)
                self.sessions_layout.addWidget(card)
        
        self.sessions_layout.addStretch()
    
    def create_session_card(self, session: ClaudeSession) -> QWidget:
        """创建会话卡片"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #F9FAFB;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # 第一行：状态 + 项目名称
        row1 = QHBoxLayout()
        row1.setSpacing(6)
        
        status = QLabel(session.status_icon)
        status.setStyleSheet("font-size: 14px;")
        row1.addWidget(status)
        
        # 显示自定义名称或位置
        display_name = session.custom_name if session.custom_name else session.project_name
        name = QLabel(display_name)
        name.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: #1F2937;
        """)
        # 限制长度 - 路径过长时省略前面部分
        if len(display_name) > 30:
            name.setText("..." + display_name[-30:])
            name.setToolTip(display_name)
        row1.addWidget(name)
        row1.addStretch()
        
        layout.addLayout(row1)
        
        # 第二行：TodoWrite进度
        if session.todos:
            progress = QLabel(session.todo_progress)
            progress.setStyleSheet("""
                font-size: 11px;
                color: #6B7280;
            """)
            # 限制长度
            progress_text = session.todo_progress
            if len(progress_text) > 40:
                progress.setText(progress_text[:40] + "...")
                progress.setToolTip(progress_text)
            layout.addWidget(progress)
        
        return card
    
    def show_at_cursor(self):
        """在鼠标位置显示"""
        from PyQt6.QtGui import QCursor
        cursor_pos = QCursor.pos()
        
        logger.info(f"准备显示弹出窗口，鼠标位置: ({cursor_pos.x()}, {cursor_pos.y()})")
        
        # 调整位置，确保窗口在屏幕内
        x = cursor_pos.x() - self.width() // 2
        y = cursor_pos.y() - self.height() - 10
        
        # 确保不超出屏幕
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        
        if x < 0:
            x = 0
        elif x + self.width() > screen.width():
            x = screen.width() - self.width()
        
        if y < 0:
            y = cursor_pos.y() + 10
        
        logger.info(f"弹出窗口位置: ({x}, {y}), 大小: ({self.width()}, {self.height()})")
        logger.info(f"屏幕大小: ({screen.width()}, {screen.height()})")
        
        self.move(x, y)
        self.show()
        self.raise_()
        # 不调用activateWindow()，避免切换焦点
        
        logger.info(f"弹出窗口已显示，isVisible: {self.isVisible()}, isHidden: {self.isHidden()}")
    
    def focusOutEvent(self, event):
        """失去焦点时隐藏"""
        self.hide()
        super().focusOutEvent(event)
