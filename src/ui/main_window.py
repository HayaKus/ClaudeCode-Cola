"""
主窗口模块
"""
from pathlib import Path
from typing import List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QListWidget, QListWidgetItem, QLabel,
    QToolBar, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QPixmap

from src.data.models import Session, TodoStatus
from src.data.config import Config
from src.utils.logger import logger
from src.ui.path_delegate import PathItemDelegate


class MainWindow(QMainWindow):
    """主窗口类"""

    # 信号定义
    session_selected = pyqtSignal(str)  # 会话被选中
    refresh_requested = pyqtSignal()     # 请求刷新
    pin_toggled = pyqtSignal(str, bool)  # 标记切换
    session_renamed = pyqtSignal(str, str)  # 会话重命名 (session_id, new_name)

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.sessions: List[Session] = []
        self.current_session: Optional[Session] = None

        # 加载来源图标
        self.load_source_icons()

        self.init_ui()
        self.restore_state()

    def load_source_icons(self):
        """加载 Claude Code 和 Qoder 的图标"""
        try:
            # 获取图标路径
            icon_dir = Path(__file__).parent.parent.parent / "pic" / "icon"

            claude_icon_path = icon_dir / "claude_code_icon.png"
            qoder_icon_path = icon_dir / "qoder.png"

            # 加载图标并缩放到合适大小
            self.claude_icon = QIcon(str(claude_icon_path))
            self.qoder_icon = QIcon(str(qoder_icon_path))

            logger.info(f"成功加载来源图标: {icon_dir}")
        except Exception as e:
            logger.error(f"加载来源图标失败: {e}")
            # 如果加载失败,使用默认图标
            self.claude_icon = QIcon()
            self.qoder_icon = QIcon()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("ClaudeCode-Cola 🥤")
        self.setMinimumSize(1000, 600)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建主布局
        self.create_main_layout()

        # 应用主题
        self.apply_theme()

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        refresh_action = QAction("刷新", self)
        refresh_action.setShortcut("Cmd+R")
        refresh_action.triggered.connect(self.on_refresh)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        quit_action = QAction("退出", self)
        quit_action.setShortcut("Cmd+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图")

        active_only_action = QAction("仅显示活跃会话", self)
        active_only_action.setCheckable(True)
        active_only_action.triggered.connect(self.toggle_active_only)
        view_menu.addAction(active_only_action)

        pinned_only_action = QAction("仅显示标记会话", self)
        pinned_only_action.setCheckable(True)
        pinned_only_action.triggered.connect(self.toggle_pinned_only)
        view_menu.addAction(pinned_only_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)


    def create_main_layout(self):
        """创建主布局 - 匹配命令行版本的垂直布局"""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # === 1. Header: 标题 ===
        header = self.create_header()
        main_layout.addWidget(header, stretch=0)

        # === 2. Stats: 统计面板 (4列) ===
        stats = self.create_stats_panel()
        main_layout.addWidget(stats, stretch=0)

        # === 3. Main: 会话表格 ===
        sessions_widget = self.create_sessions_table()
        main_layout.addWidget(sessions_widget, stretch=1)

        self.setCentralWidget(central_widget)

    def create_header(self) -> QWidget:
        """创建标题栏"""
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0066CC, stop:1 #0052A3);
                border-radius: 12px;
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(12)
        
        title = QLabel("🥤 ClaudeCode-Cola")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: 600; background: transparent;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # 添加版本号标签（移到最右边）
        version = QLabel("v1.0.1")
        version.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: 500;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 4px 12px;
        """)
        layout.addWidget(version)

        header.setMaximumHeight(52)
        header.setMinimumHeight(52)
        return header

    def create_stats_panel(self) -> QWidget:
        """创建统计面板 - 4列统计"""
        stats = QWidget()
        stats.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(stats)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建4个统计标签 - 使用统一的蓝色主题
        self.stats_total = self.create_stat_label("总会话数", "0", "#0066CC")
        self.stats_active = self.create_stat_label("活跃会话", "0", "#10B981")
        self.stats_todos = self.create_stat_label("TodoWrite项目", "0", "#0066CC")
        self.stats_pending = self.create_stat_label("待完成任务", "0", "#6B7280")

        layout.addWidget(self.stats_total, 1)
        layout.addWidget(self.stats_active, 1)
        layout.addWidget(self.stats_todos, 1)
        layout.addWidget(self.stats_pending, 1)

        stats.setMaximumHeight(90)
        stats.setMinimumHeight(90)
        return stats

    def create_stat_label(self, title: str, value: str, color: str = "#0066CC") -> QWidget:
        """创建单个统计标签"""
        widget = QWidget()
        widget.setStyleSheet("""
            background: white;
            border: 2px solid #E8F4FF;
            border-radius: 12px;
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 32px; font-weight: 700; color: {color}; background: transparent; border: none;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setObjectName("value")  # 用于后续更新

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #6B7280; background: transparent; border: none; font-weight: 500;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(value_label)
        layout.addWidget(title_label)

        return widget

    def create_sessions_table(self) -> QWidget:
        """创建会话表格"""
        container = QFrame()
        container.setFrameShape(QFrame.Shape.StyledPanel)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # 表格（新增来源列）
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(6)
        self.sessions_table.setHorizontalHeaderLabels(["状态", "来源", "项目", "位置", "TodoWrite进度", "会话ID"])

        # 设置图标大小
        self.sessions_table.setIconSize(QSize(24, 24))

        # 设置列宽
        header = self.sessions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 80)  # 状态图标列
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 60)  # 来源图标列（图标不需要太宽）
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.resizeSection(2, 180)  # 项目名称列
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.resizeSection(3, 220)  # 位置列
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # TodoWrite进度列

        # 隐藏会话ID列
        self.sessions_table.setColumnHidden(5, True)

        # 为位置列(列3)设置自定义委托,使路径从前面省略
        path_delegate = PathItemDelegate(self.sessions_table)
        self.sessions_table.setItemDelegateForColumn(3, path_delegate)

        # 垂直表头
        self.sessions_table.verticalHeader().setVisible(False)

        # 选择模式
        self.sessions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sessions_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # 启用右键菜单
        self.sessions_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sessions_table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.sessions_table)

        return container

    def create_todos_panel(self) -> QWidget:
        """创建Todo汇总面板"""
        container = QFrame()
        container.setFrameShape(QFrame.Shape.StyledPanel)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)

        # 标题和统计信息放在同一行
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # 标题
        title = QLabel("📝 TodoWrite 汇总")
        title.setStyleSheet("font-size: 14px; font-weight: bold; border: none;")
        header_layout.addWidget(title)
        
        # 统计信息
        self.todos_stats = QLabel("暂无任务")
        self.todos_stats.setStyleSheet("font-size: 12px; color: #666666; border: none;")
        header_layout.addWidget(self.todos_stats)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)

        # 任务列表
        self.todos_list = QTextEdit()
        self.todos_list.setReadOnly(True)
        self.todos_list.setStyleSheet("""
            QTextEdit {
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                background-color: #FAFAFA;
            }
        """)
        layout.addWidget(self.todos_list)

        return container

    def create_footer(self) -> QWidget:
        """创建底部信息栏"""
        footer = QWidget()
        footer.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #E5E5EA;
                border-radius: 5px;
            }
        """)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(10, 5, 10, 5)

        layout.addStretch()

        # 快捷键提示
        shortcuts = QLabel("快捷键: ⌘R 刷新 | ⌘Q 退出")
        shortcuts.setStyleSheet("font-size: 10px; color: #8E8E93; background: transparent;")
        layout.addWidget(shortcuts)

        footer.setMaximumHeight(28)
        footer.setMinimumHeight(28)
        return footer

    def apply_theme(self):
        """应用主题"""
        # 基础样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F2F2F7;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: none;
                font-size: 13px;
                gridline-color: #E5E5EA;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F2F2F7;
            }
            QTableWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #F2F2F7;
            }
            QHeaderView::section {
                background-color: #f9fafb;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                font-weight: 600;
                font-size: 12px;
                color: #374151;
            }
            QToolBar {
                background-color: #F5F5F7;
                border-bottom: 1px solid #D1D1D6;
                spacing: 10px;
                padding: 5px;
            }
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #D1D1D6;
                border-radius: 5px;
                background-color: white;
            }
            QProgressBar {
                border: 1px solid #D1D1D6;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #34C759;
                border-radius: 5px;
            }
        """)

    def update_sessions(self, sessions: List[Session]):
        """更新会话列表"""
        self.sessions = sessions
        self.refresh_sessions_display()

    def refresh_sessions_display(self):
        """刷新会话表格显示"""
        # 清空表格
        self.sessions_table.setRowCount(0)

        # 显示活跃会话和被标记的会话（和CLI版本保持一致）
        displayed_sessions = []
        for session in self.sessions:
            if session.is_active or session.is_pinned:
                displayed_sessions.append(session)

        # 排序：标记的在前，最后活动时间倒序（与命令行版本保持一致）
        sorted_sessions = sorted(
            displayed_sessions,
            key=lambda s: (s.is_pinned, s.last_activity),
            reverse=True
        )

        # 只显示前20个会话（和CLI版本保持一致）
        sorted_sessions = sorted_sessions[:20]

        # 填充表格
        for row, session in enumerate(sorted_sessions):
            self.sessions_table.insertRow(row)

            # 列0: 状态图标
            status_item = QTableWidgetItem(session.status_icon)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sessions_table.setItem(row, 0, status_item)

            # 列1: 来源标识（使用图标）
            source_item = QTableWidgetItem()
            if session.source_type == "claude":
                source_item.setIcon(self.claude_icon)
                source_item.setToolTip("Claude Code")
            else:
                source_item.setIcon(self.qoder_icon)
                source_item.setToolTip("Qoder CLI")
            source_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sessions_table.setItem(row, 1, source_item)

            # 列2: 项目名称（自定义名称或默认为空）
            custom_name = session.custom_name if session.custom_name else ""
            name_item = QTableWidgetItem(custom_name)
            self.sessions_table.setItem(row, 2, name_item)

            # 列3: 位置（原项目路径）
            location_item = QTableWidgetItem(session.project_name)
            self.sessions_table.setItem(row, 3, location_item)

            # 列4: TodoWrite进度（直接使用格式化字符串）
            progress_text = session.todo_progress
            progress_item = QTableWidgetItem(progress_text)
            self.sessions_table.setItem(row, 4, progress_item)

            # 列5: 会话ID（统一显示前20个字符）
            session_id_display = session.session_id[:20] + "..." if len(session.session_id) > 20 else session.session_id
            id_item = QTableWidgetItem(session_id_display)
            id_item.setFont(self.sessions_table.font())
            id_item.setToolTip(session.session_id)  # 完整ID显示在tooltip中
            self.sessions_table.setItem(row, 5, id_item)

            # 设置行高
            self.sessions_table.setRowHeight(row, 40)

        # 更新统计面板（使用过滤后的会话）
        self.update_stats(sorted_sessions)

        logger.info(f"刷新会话表格: 扫描 {len(self.sessions)} 个会话，显示 {len(sorted_sessions)} 个（活跃/标记）")

    def update_stats(self, displayed_sessions: List[Session] = None):
        """更新统计面板"""
        # 使用过滤后的会话列表进行统计
        sessions_to_count = displayed_sessions if displayed_sessions is not None else self.sessions

        total = len(sessions_to_count)
        active = sum(1 for s in sessions_to_count if s.is_active)
        todo_projects = sum(1 for s in sessions_to_count if s.todos)
        pending_todos = sum(
            len([t for t in s.todos if t.status.value == 'pending'])
            for s in sessions_to_count
        )

        # 更新统计标签
        self.stats_total.findChild(QLabel, "value").setText(str(total))
        self.stats_active.findChild(QLabel, "value").setText(str(active))
        self.stats_todos.findChild(QLabel, "value").setText(str(todo_projects))
        self.stats_pending.findChild(QLabel, "value").setText(str(pending_todos))

    def update_todos_summary(self, displayed_sessions: List[Session] = None):
        """更新TodoWrite汇总面板"""
        # 使用过滤后的会话列表进行统计
        sessions_to_count = displayed_sessions if displayed_sessions is not None else self.sessions

        # 统计所有任务
        all_todos = []
        completed = 0
        in_progress = 0
        pending = 0

        for session in sessions_to_count:
            for todo in session.todos:
                all_todos.append((session.project_name, todo))
                if todo.status.value == 'completed':
                    completed += 1
                elif todo.status.value == 'in_progress':
                    in_progress += 1
                elif todo.status.value == 'pending':
                    pending += 1

        # 更新统计信息
        total = len(all_todos)
        if total > 0:
            stats_text = f"✅ 已完成: {completed} | 🔄 进行中: {in_progress} | ⏳ 待处理: {pending}"
            self.todos_stats.setText(stats_text)

            # 显示最新的10个任务
            todos_text = ""
            for project, todo in all_todos[:10]:
                todos_text += f"{todo}\n[{project}]\n\n"

            if len(all_todos) > 10:
                todos_text += f"\n... 还有 {len(all_todos) - 10} 个任务"

            self.todos_list.setText(todos_text)
        else:
            self.todos_stats.setText("暂无任务")
            self.todos_list.setText("暂无 TodoWrite 任务")

    def on_refresh(self):
        """刷新按钮点击"""
        logger.info("用户请求刷新")
        self.refresh_requested.emit()


    def toggle_active_only(self, checked: bool):
        """切换仅显示活跃会话"""
        # 需要重新过滤显示
        for row, session in enumerate(self.sessions):
            if checked:
                self.sessions_table.setRowHidden(row, not session.is_active)
            else:
                self.sessions_table.setRowHidden(row, False)

    def toggle_pinned_only(self, checked: bool):
        """切换仅显示标记会话"""
        # 需要重新过滤显示
        for row, session in enumerate(self.sessions):
            if checked:
                self.sessions_table.setRowHidden(row, not session.is_pinned)
            else:
                self.sessions_table.setRowHidden(row, False)

    def show_context_menu(self, position):
        """显示右键菜单"""
        from PyQt6.QtWidgets import QMenu
        
        # 获取点击的行
        row = self.sessions_table.rowAt(position.y())
        if row < 0:
            return
        
        # 获取对应的会话
        # 需要从显示的会话列表中获取
        displayed_sessions = []
        for session in self.sessions:
            if session.is_active or session.is_pinned:
                displayed_sessions.append(session)
        
        sorted_sessions = sorted(
            displayed_sessions,
            key=lambda s: (s.is_pinned, s.last_activity),
            reverse=True
        )[:20]
        
        if row >= len(sorted_sessions):
            return
        
        session = sorted_sessions[row]
        
        # 创建右键菜单
        menu = QMenu(self)
        
        # 根据会话的标记状态显示不同的菜单项
        if session.is_pinned:
            action = menu.addAction("📌 取消标记")
            action.triggered.connect(lambda: self.toggle_pin_session(session.session_id, False))
        else:
            action = menu.addAction("📌 标记会话")
            action.triggered.connect(lambda: self.toggle_pin_session(session.session_id, True))
        
        # 添加分隔线
        menu.addSeparator()
        
        # 添加重命名项目功能
        rename_action = menu.addAction("✏️ 重命名项目")
        rename_action.triggered.connect(lambda: self.rename_session(session.session_id, session.custom_name))
        
        # 添加复制会话ID功能
        copy_action = menu.addAction("📋 复制会话ID")
        copy_action.triggered.connect(lambda: self.copy_session_id(session.session_id))
        
        # 如果有TodoWrite任务，添加查看详情功能
        if session.todos:
            menu.addSeparator()
            view_todos_action = menu.addAction("📝 查看TodoWrite详情")
            view_todos_action.triggered.connect(lambda: self.show_todo_details(session))
        
        # 显示菜单
        menu.exec(self.sessions_table.viewport().mapToGlobal(position))
    
    def toggle_pin_session(self, session_id: str, pin: bool):
        """切换会话标记状态"""
        logger.info(f"{'标记' if pin else '取消标记'}会话: {session_id}")
        
        # 发送信号通知应用层处理
        self.pin_toggled.emit(session_id, pin)
    
    def rename_session(self, session_id: str, current_name: str):
        """重命名会话项目"""
        from PyQt6.QtWidgets import QInputDialog
        
        # 显示输入对话框
        new_name, ok = QInputDialog.getText(
            self,
            "重命名项目",
            "请输入新的项目名称：",
            text=current_name
        )
        
        if ok and new_name != current_name:
            logger.info(f"重命名会话 {session_id}: {current_name} -> {new_name}")
            # 发送信号通知应用层处理
            self.session_renamed.emit(session_id, new_name)
    
    def copy_session_id(self, session_id: str):
        """复制会话ID到剪贴板"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(session_id)
        logger.info(f"已复制会话ID到剪贴板: {session_id}")
    
    def show_todo_details(self, session: Session):
        """显示TodoWrite详情对话框"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"TodoWrite详情 - {session.custom_name or session.project_name}")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 创建文本编辑器显示任务详情
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 13px;
                background-color: #F9FAFB;
                border: 1px solid #E5E5EA;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        # 统计信息
        total = len(session.todos)
        completed = sum(1 for t in session.todos if t.status == TodoStatus.COMPLETED)
        in_progress = sum(1 for t in session.todos if t.status == TodoStatus.IN_PROGRESS)
        pending = sum(1 for t in session.todos if t.status == TodoStatus.PENDING)
        
        content = f"📊 任务统计\n"
        content += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        content += f"总任务数: {total}\n"
        content += f"✅ 已完成: {completed}\n"
        content += f"🔄 进行中: {in_progress}\n"
        content += f"⏳ 待处理: {pending}\n"
        content += f"\n📝 任务列表\n"
        content += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # 格式化任务列表
        for i, todo in enumerate(session.todos, 1):
            content += f"{i}. {todo.status_icon} {todo.content}\n"
        
        text_edit.setText(content)
        layout.addWidget(text_edit)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("关闭")
        close_button.setStyleSheet("""
            QPushButton {
                background: #0066CC;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #0052A3;
            }
        """)
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
        logger.info(f"显示TodoWrite详情: {session.session_id}")

    def show_about(self):
        """显示关于对话框"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "关于 ClaudeCode-Cola",
            "ClaudeCode-Cola 🥤\n\n"
            "版本: 1.0.1\n"
            "作者: 哈雅 (工号: 263321)\n\n"
            "一个用于监控 Claude Code 会话和 TodoWrite 任务的 Mac 应用"
        )

    def restore_state(self):
        """恢复窗口状态"""
        if self.config.window_x and self.config.window_y:
            self.move(self.config.window_x, self.config.window_y)

        self.resize(self.config.window_width, self.config.window_height)

    def closeEvent(self, event):
        """窗口关闭事件 - 关闭窗口时隐藏到后台，不退出应用"""
        # 保存窗口状态
        self.config.window_x = self.x()
        self.config.window_y = self.y()
        self.config.window_width = self.width()
        self.config.window_height = self.height()
        self.config.save()

        # 检查是否设置了删除标志（真正退出）
        if self.testAttribute(Qt.WidgetAttribute.WA_DeleteOnClose):
            # 真正退出，接受关闭事件
            event.accept()
            logger.info("主窗口已关闭")
        else:
            # 隐藏窗口而不是关闭应用
            event.ignore()
            self.hide()
            logger.info("主窗口已隐藏到后台")
