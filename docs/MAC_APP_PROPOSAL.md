# ClaudeCode-Cola Mac 应用技术方案

> **选定方案：** PyQt6
> **版本：** v2.0 - 技术实施版
> **日期：** 2025-11-17
> **作者：** 哈雅 (工号: 263321)

---

## 📋 项目概述

将现有的命令行工具 **ClaudeCode-Cola** 转换为原生 Mac 应用程序，使用 **PyQt6** 框架，提供现代化的图形界面和更好的用户体验。

### 为什么选择 PyQt6

✅ **技术优势：**
- 可复用现有 90% 的 Python 代码
- 完全原生的 Mac UI 体验
- 丰富的 UI 组件和成熟的生态系统
- 性能优秀，资源占用合理
- 跨平台能力（未来可拓展）

✅ **开发优势：**
- 开发周期短（3-4周）
- 学习曲线适中
- 调试工具完善
- 社区活跃，文档齐全

---

## 🎯 功能规划

### 保留功能（从命令行版本）
- ✅ 全局监控所有 Claude Code 会话
- ✅ 实时显示 TodoWrite 任务状态
- ✅ 会话活跃状态检测
- ✅ 会话标记（Pin/Unpin）功能
- ✅ 实时文件系统监控
- ✅ 统计面板显示

### 新增功能
- 🎨 现代化的 Mac 原生 UI
- 📊 菜单栏（Menu Bar）常驻图标
- 🔔 系统通知集成（macOS Notification Center）
- ⚙️ 图形化设置界面
- 🔍 强大的搜索和筛选功能
- 📱 全局快捷键支持
- 🌓 深色/浅色模式自动适配
- 💾 会话导出和备份功能
- 📂 一键跳转到项目目录
- 🔄 自动刷新与手动刷新切换

---

## 🏗 技术架构设计

### 整体架构

```
┌─────────────────────────────────────────────┐
│           ClaudeCode-Cola.app               │
├─────────────────────────────────────────────┤
│  UI Layer (PyQt6)                           │
│  ├── MainWindow        - 主窗口             │
│  ├── SystemTray        - 菜单栏图标         │
│  ├── SettingsDialog    - 设置对话框         │
│  ├── SessionWidget     - 会话展示组件       │
│  └── TodoWidget        - TodoWrite组件      │
├─────────────────────────────────────────────┤
│  Business Logic Layer (复用现有代码)        │
│  ├── SessionMonitor    - 会话监控器         │
│  ├── FileWatcher       - 文件系统监听       │
│  ├── ProcessDetector   - 进程检测器         │
│  ├── TodoParser        - Todo解析器         │
│  └── DataManager       - 数据管理器         │
├─────────────────────────────────────────────┤
│  Data Layer                                 │
│  ├── SQLite Database   - 会话/Todo持久化   │
│  ├── Config Manager    - 配置管理           │
│  └── Cache Manager     - 缓存管理           │
└─────────────────────────────────────────────┘
```

### 项目文件结构

```
ClaudeCode-Cola/
├── src/                              # 源代码目录
│   ├── main.py                       # 应用入口
│   ├── app.py                        # 应用主类
│   │
│   ├── ui/                           # UI 层
│   │   ├── __init__.py
│   │   ├── main_window.py            # 主窗口
│   │   ├── system_tray.py            # 系统托盘
│   │   ├── settings_dialog.py        # 设置对话框
│   │   ├── widgets/                  # 自定义组件
│   │   │   ├── session_widget.py     # 会话卡片组件
│   │   │   ├── todo_widget.py        # Todo列表组件
│   │   │   ├── status_badge.py       # 状态徽章组件
│   │   │   └── search_bar.py         # 搜索栏组件
│   │   └── themes/                   # 主题样式
│   │       ├── light.qss             # 浅色主题
│   │       └── dark.qss              # 深色主题
│   │
│   ├── core/                         # 业务逻辑层（复用现有）
│   │   ├── __init__.py
│   │   ├── session_monitor.py        # 会话监控（改造自现有代码）
│   │   ├── file_watcher.py           # 文件监听（改造自现有代码）
│   │   ├── process_detector.py       # 进程检测（复用现有）
│   │   ├── todo_parser.py            # Todo解析器
│   │   └── notification_manager.py   # 通知管理器
│   │
│   ├── data/                         # 数据层
│   │   ├── __init__.py
│   │   ├── database.py               # SQLite数据库
│   │   ├── models.py                 # 数据模型
│   │   ├── config.py                 # 配置管理
│   │   └── cache.py                  # 缓存管理
│   │
│   └── utils/                        # 工具函数
│       ├── __init__.py
│       ├── logger.py                 # 日志工具
│       ├── constants.py              # 常量定义
│       └── helpers.py                # 辅助函数
│
├── resources/                        # 资源文件
│   ├── icons/                        # 图标资源
│   │   ├── app.icns                  # 应用图标
│   │   ├── tray_active.png           # 托盘图标-活跃
│   │   ├── tray_inactive.png         # 托盘图标-非活跃
│   │   └── tray_error.png            # 托盘图标-错误
│   └── fonts/                        # 字体（如需要）
│
├── tests/                            # 测试代码
│   ├── test_ui.py
│   ├── test_core.py
│   └── test_data.py
│
├── scripts/                          # 辅助脚本
│   ├── build.sh                      # 构建脚本
│   └── install_deps.sh               # 依赖安装脚本
│
├── docs/                             # 文档
│   └── MAC_APP_PROPOSAL.md           # 本文档
│
├── setup.py                          # py2app 打包配置
├── requirements.txt                  # Python 依赖
├── requirements-dev.txt              # 开发依赖
└── README.md                         # 项目说明
```

---

## 💻 核心模块详细设计

### 1. 主窗口 (MainWindow)

**文件：** `src/ui/main_window.py`

**功能职责：**
- 展示会话列表和详情
- 提供搜索和筛选功能
- 响应用户交互
- 管理窗口状态

**核心代码结构：**

```python
from PyQt6.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

class MainWindow(QMainWindow):
    """主窗口类"""

    # 信号定义
    session_selected = pyqtSignal(str)  # 会话被选中
    refresh_requested = pyqtSignal()     # 请求刷新
    pin_toggled = pyqtSignal(str, bool)  # 标记切换

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_connections()
        self.restore_state()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("ClaudeCode-Cola 🥤")
        self.setMinimumSize(1000, 600)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建工具栏
        self.create_toolbar()

        # 创建主布局（分割视图）
        self.create_main_layout()

        # 应用样式表
        self.apply_theme()

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")
        file_menu.addAction("刷新", self.on_refresh, "Cmd+R")
        file_menu.addAction("导出会话", self.on_export)
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close, "Cmd+Q")

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        edit_menu.addAction("搜索", self.on_search, "Cmd+F")
        edit_menu.addAction("标记会话", self.on_pin, "Cmd+P")

        # 视图菜单
        view_menu = menubar.addMenu("视图")
        view_menu.addAction("仅显示活跃会话", self.toggle_active_only)
        view_menu.addAction("仅显示标记会话", self.toggle_pinned_only)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        help_menu.addAction("关于", self.show_about)

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = self.addToolBar("主工具栏")
        toolbar.setMovable(False)

        # 刷新按钮
        refresh_action = toolbar.addAction("🔄 刷新")
        refresh_action.triggered.connect(self.on_refresh)

        # 设置按钮
        settings_action = toolbar.addAction("⚙️ 设置")
        settings_action.triggered.connect(self.show_settings)

        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        # 搜索框
        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self.on_search_changed)
        toolbar.addWidget(self.search_bar)

    def create_main_layout(self):
        """创建主布局"""
        # 分割器
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：会话列表
        self.session_list = SessionListWidget()
        self.session_list.session_selected.connect(self.on_session_selected)
        splitter.addWidget(self.session_list)

        # 右侧：详情面板
        self.detail_panel = DetailPanel()
        splitter.addWidget(self.detail_panel)

        # 设置分割比例
        splitter.setStretchFactor(0, 1)  # 左侧占1份
        splitter.setStretchFactor(1, 2)  # 右侧占2份

        self.setCentralWidget(splitter)

    def apply_theme(self):
        """应用主题"""
        theme = self.get_current_theme()
        with open(f"src/ui/themes/{theme}.qss", "r") as f:
            self.setStyleSheet(f.read())
```

### 2. 系统托盘 (SystemTray)

**文件：** `src/ui/system_tray.py`

**功能职责：**
- 常驻菜单栏
- 显示状态指示
- 提供快捷操作
- 发送通知

**核心代码结构：**

```python
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal

class SystemTray(QSystemTrayIcon):
    """系统托盘类"""

    # 信号
    show_window_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        # 初始化图标（默认活跃状态）
        icon = QIcon("resources/icons/tray_active.png")
        super().__init__(icon, parent)

        self.setup_menu()
        self.setup_connections()

    def setup_menu(self):
        """设置右键菜单"""
        menu = QMenu()

        # 显示主窗口
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show_window_requested)
        menu.addAction(show_action)

        menu.addSeparator()

        # 活跃会话子菜单（动态生成）
        self.active_sessions_menu = menu.addMenu("活跃会话")
        self.update_active_sessions_menu([])

        menu.addSeparator()

        # 刷新
        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self.refresh_requested)
        menu.addAction(refresh_action)

        # 设置
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_requested)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def update_status(self, active_count: int, waiting_count: int, error_count: int):
        """更新托盘图标状态"""
        if error_count > 0:
            icon_path = "resources/icons/tray_error.png"
            tooltip = f"❌ {error_count} 个会话出错"
        elif waiting_count > 0:
            icon_path = "resources/icons/tray_inactive.png"
            tooltip = f"🟡 {waiting_count} 个会话需要关注"
        else:
            icon_path = "resources/icons/tray_active.png"
            tooltip = f"🟢 全部活跃 ({active_count})"

        self.setIcon(QIcon(icon_path))
        self.setToolTip(f"ClaudeCode-Cola\n{tooltip}")

    def update_active_sessions_menu(self, sessions: list):
        """更新活跃会话子菜单"""
        self.active_sessions_menu.clear()

        if not sessions:
            no_sessions = QAction("(无活跃会话)", self)
            no_sessions.setEnabled(False)
            self.active_sessions_menu.addAction(no_sessions)
            return

        for session in sessions[:10]:  # 最多显示10个
            status_icon = "🟢" if session.is_active else "🟡"
            action = QAction(
                f"{status_icon} {session.project_name}",
                self
            )
            action.triggered.connect(
                lambda s=session: self.open_session(s)
            )
            self.active_sessions_menu.addAction(action)

    def show_notification(self, title: str, message: str, notification_type: str = "info"):
        """显示系统通知"""
        icon_map = {
            "info": QSystemTrayIcon.MessageIcon.Information,
            "warning": QSystemTrayIcon.MessageIcon.Warning,
            "error": QSystemTrayIcon.MessageIcon.Critical,
        }

        icon = icon_map.get(notification_type, QSystemTrayIcon.MessageIcon.Information)
        self.showMessage(title, message, icon, 3000)  # 显示3秒
```

### 3. 会话监控器 (SessionMonitor)

**文件：** `src/core/session_monitor.py`

**功能职责：**
- 监控会话文件变化
- 解析会话数据
- 检测进程状态
- 触发数据更新

**核心代码结构：**

```python
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil

from ..data.models import ClaudeSession, TodoItem
from ..utils.logger import logger

class SessionMonitor:
    """会话监控器（改造自现有 claudecode_cola.py）"""

    def __init__(self, projects_dir: Path):
        self.projects_dir = projects_dir
        self.sessions: Dict[str, ClaudeSession] = {}
        self.observer = Observer()

        # 文件监听处理器
        self.file_handler = SessionFileHandler(self)

    async def start(self):
        """启动监控"""
        logger.info("启动会话监控器...")

        # 初始扫描
        await self.scan_all_sessions()

        # 启动文件监听
        self.observer.schedule(
            self.file_handler,
            str(self.projects_dir),
            recursive=True
        )
        self.observer.start()

        logger.info(f"监控已启动，找到 {len(self.sessions)} 个会话")

    async def scan_all_sessions(self):
        """扫描所有会话文件"""
        jsonl_files = list(self.projects_dir.rglob("*.jsonl"))

        for file_path in jsonl_files:
            await self.process_session_file(file_path)

    async def process_session_file(self, file_path: Path):
        """处理单个会话文件"""
        session_id = file_path.stem

        try:
            # 读取并解析会话数据
            session_data = await self.parse_session_file(file_path)

            # 检测进程状态
            is_active = self.check_process_active(session_id)

            # 创建或更新会话对象
            session = ClaudeSession(
                session_id=session_id,
                project_path=str(file_path.parent),
                project_name=file_path.parent.name,
                **session_data,
                is_active=is_active
            )

            self.sessions[session_id] = session

        except Exception as e:
            logger.error(f"处理会话文件失败 {file_path}: {e}")

    async def parse_session_file(self, file_path: Path) -> dict:
        """解析会话文件（复用现有逻辑）"""
        todos = []
        messages = []
        start_time = None
        last_activity = None

        async with aiofiles.open(file_path, 'r') as f:
            async for line in f:
                try:
                    data = json.loads(line)

                    # 解析时间戳
                    ts = datetime.fromisoformat(data.get('ts', ''))
                    if not start_time:
                        start_time = ts
                    last_activity = ts

                    # 解析 TodoWrite
                    if 'todo' in data:
                        todo = TodoItem(**data['todo'])
                        todos.append(todo)

                    # 解析消息
                    if 'message' in data:
                        messages.append(data['message'])

                except json.JSONDecodeError:
                    continue

        return {
            'todos': todos,
            'start_time': start_time,
            'last_activity': last_activity,
            'message_count': len(messages),
            'last_message': messages[-1] if messages else ""
        }

    def check_process_active(self, session_id: str) -> bool:
        """检查进程是否活跃（复用现有逻辑）"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and session_id in ' '.join(cmdline):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
```

### 4. 数据模型 (Models)

**文件：** `src/data/models.py`

**数据模型定义：**

```python
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
        return self.status == TodoStatus.COMPLETED

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
    todos: List[TodoItem] = field(default_factory=list)
    message_count: int = 0
    last_message: str = ""
    file_path: str = ""

    @property
    def duration(self) -> str:
        """会话持续时间"""
        delta = datetime.now() - self.start_time
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"

    @property
    def todo_progress(self) -> tuple:
        """Todo进度 (完成数, 总数)"""
        completed = sum(1 for t in self.todos if t.is_completed)
        return (completed, len(self.todos))

    @property
    def status_color(self) -> str:
        """状态颜色"""
        if not self.is_active:
            return "warning"  # 黄色
        if self.has_errors:
            return "error"    # 红色
        return "success"      # 绿色
```

---

## 🎨 UI/UX 设计

### 主题样式 (QSS)

**浅色主题：** `src/ui/themes/light.qss`

```css
/* 主窗口 */
QMainWindow {
    background-color: #FFFFFF;
}

/* 工具栏 */
QToolBar {
    background-color: #F5F5F7;
    border-bottom: 1px solid #D1D1D6;
    spacing: 10px;
    padding: 5px;
}

/* 会话列表 */
QListWidget {
    background-color: #FFFFFF;
    border: none;
    border-right: 1px solid #D1D1D6;
}

QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #F2F2F7;
}

QListWidget::item:selected {
    background-color: #007AFF;
    color: white;
}

QListWidget::item:hover {
    background-color: #F2F2F7;
}

/* 按钮 */
QPushButton {
    background-color: #007AFF;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #0051D5;
}

QPushButton:pressed {
    background-color: #004BB5;
}

/* 状态徽章 */
.StatusBadge {
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: bold;
}

.StatusBadge[status="active"] {
    background-color: #34C759;
    color: white;
}

.StatusBadge[status="inactive"] {
    background-color: #FF9500;
    color: white;
}

.StatusBadge[status="error"] {
    background-color: #FF3B30;
    color: white;
}
```

### 快捷键映射

```python
# src/ui/shortcuts.py

SHORTCUTS = {
    # 全局快捷键
    "Cmd+R": "刷新",
    "Cmd+F": "搜索",
    "Cmd+P": "标记当前会话",
    "Cmd+,": "打开设置",
    "Cmd+W": "关闭窗口",
    "Cmd+Q": "退出应用",
    "Cmd+N": "新建会话",

    # 导航快捷键
    "Cmd+1": "切换到会话列表",
    "Cmd+2": "切换到Todo详情",
    "Cmd+3": "切换到消息历史",

    # 列表操作
    "Up/Down": "上下选择",
    "Enter": "打开选中会话",
    "Space": "标记/取消标记",
    "Delete": "删除会话记录",
}
```

---

## 📦 打包和分发

### py2app 配置

**文件：** `setup.py`

```python
from setuptools import setup

APP = ['src/main.py']
DATA_FILES = [
    ('resources/icons', [
        'resources/icons/app.icns',
        'resources/icons/tray_active.png',
        'resources/icons/tray_inactive.png',
        'resources/icons/tray_error.png',
    ]),
    ('src/ui/themes', [
        'src/ui/themes/light.qss',
        'src/ui/themes/dark.qss',
    ]),
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'resources/icons/app.icns',
    'plist': {
        'CFBundleName': 'ClaudeCode-Cola',
        'CFBundleDisplayName': 'ClaudeCode-Cola',
        'CFBundleIdentifier': 'com.haya.claudecode-cola',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,  # 菜单栏应用
        'NSHighResolutionCapable': True,  # 支持Retina
        'LSMinimumSystemVersion': '10.15.0',  # 最低系统版本
        'NSHumanReadableCopyright': 'Copyright © 2025 哈雅',
    },
    'packages': [
        'PyQt6',
        'watchdog',
        'psutil',
        'aiofiles',
        'dateutil',
    ],
    'includes': [
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    'excludes': [
        'PyQt6.QtWebEngine',  # 不需要的模块
        'PyQt6.QtNetwork',
        'PyQt6.QtMultimedia',
    ],
}

setup(
    name='ClaudeCode-Cola',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'PyQt6>=6.6.0',
        'watchdog>=3.0.0',
        'psutil>=5.9.0',
        'aiofiles>=23.2.0',
        'python-dateutil>=2.8.0',
    ],
)
```

### 构建脚本

**文件：** `scripts/build.sh`

```bash
#!/bin/bash

echo "🚀 开始构建 ClaudeCode-Cola Mac 应用..."

# 清理旧的构建文件
echo "📦 清理旧文件..."
rm -rf build dist

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt
pip install py2app

# 构建应用
echo "🔨 构建应用..."
python setup.py py2app

# 代码签名（可选）
if [ -n "$SIGNING_IDENTITY" ]; then
    echo "✍️ 代码签名..."
    codesign --deep --force --verify --verbose \
        --sign "$SIGNING_IDENTITY" \
        dist/ClaudeCode-Cola.app
fi

# 完成
echo "✅ 构建完成！"
echo "📍 应用位置: dist/ClaudeCode-Cola.app"
echo ""
echo "💡 测试应用:"
echo "   open dist/ClaudeCode-Cola.app"
```

---

## 📅 开发计划

### 第一阶段：项目搭建（3天）

**Day 1: 环境搭建**
- [ ] 创建项目结构
- [ ] 配置虚拟环境
- [ ] 安装 PyQt6 和依赖
- [ ] 编写 Hello World 程序

**Day 2: 基础框架**
- [ ] 实现主窗口框架
- [ ] 实现系统托盘框架
- [ ] 配置主题样式
- [ ] 测试基本显示

**Day 3: 代码迁移**
- [ ] 迁移会话监控代码
- [ ] 迁移文件监听代码
- [ ] 迁移进程检测代码
- [ ] 编写数据模型

### 第二阶段：核心功能（1周）

**Day 4-5: 会话列表**
- [ ] 实现会话列表组件
- [ ] 实现会话状态显示
- [ ] 实现标记功能
- [ ] 实现搜索功能

**Day 6-7: TodoWrite展示**
- [ ] 实现Todo列表组件
- [ ] 实现进度条显示
- [ ] 实现状态图标
- [ ] 实现任务树状展示

**Day 8-10: 实时更新**
- [ ] 集成文件监听
- [ ] 实现UI自动刷新
- [ ] 实现进程状态检测
- [ ] 性能优化

### 第三阶段：增强功能（1周）

**Day 11-12: 设置面板**
- [ ] 实现设置对话框
- [ ] 实现配置保存
- [ ] 实现主题切换
- [ ] 实现路径配置

**Day 13-14: 通知系统**
- [ ] 集成系统通知
- [ ] 实现通知规则
- [ ] 实现通知设置
- [ ] 测试通知功能

**Day 15-17: 数据持久化**
- [ ] 设计数据库结构
- [ ] 实现SQLite集成
- [ ] 实现数据导入导出
- [ ] 实现缓存机制

### 第四阶段：优化测试（5天）

**Day 18-19: UI/UX优化**
- [ ] 细节打磨
- [ ] 动画效果
- [ ] 响应速度优化
- [ ] 用户体验测试

**Day 20-21: 性能优化**
- [ ] 内存优化
- [ ] 启动速度优化
- [ ] 大量会话测试
- [ ] 长时间运行测试

**Day 22: Bug修复**
- [ ] 收集问题
- [ ] 修复Bug
- [ ] 回归测试

### 第五阶段：打包发布（2天）

**Day 23: 应用打包**
- [ ] 配置 py2app
- [ ] 构建应用
- [ ] 测试打包结果
- [ ] 优化体积

**Day 24: 文档和发布**
- [ ] 编写用户文档
- [ ] 制作演示视频
- [ ] 准备发布材料

**总计：约24个工作日（3-4周）**

---

## 🔧 开发环境配置

### 依赖安装

**requirements.txt：**
```
PyQt6>=6.6.0
PyQt6-Qt6>=6.6.0
watchdog>=3.0.0
psutil>=5.9.0
aiofiles>=23.2.0
python-dateutil>=2.8.0
```

**requirements-dev.txt：**
```
pytest>=7.0.0
pytest-qt>=4.0.0
pytest-asyncio>=0.21.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
py2app>=0.28.0
```

### 初始化命令

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 运行应用（开发模式）
python src/main.py

# 运行测试
pytest tests/

# 代码格式化
black src/

# 类型检查
mypy src/
```

---

## 📊 性能指标

### 目标性能

| 指标 | 目标值 |
|------|--------|
| 启动时间 | < 2秒 |
| 内存占用（空闲） | < 100MB |
| 内存占用（1000会话） | < 300MB |
| CPU占用（空闲） | < 1% |
| 刷新延迟 | < 500ms |
| UI响应时间 | < 100ms |

### 优化策略

1. **虚拟滚动：** 会话列表只渲染可见部分
2. **延迟加载：** TodoWrite详情按需加载
3. **增量更新：** 只更新变化的UI元素
4. **后台线程：** 文件读取和解析在后台进行
5. **缓存机制：** 缓存解析结果，避免重复计算

---

## ⚠️ 风险控制

### 技术风险

| 风险项 | 可能性 | 影响 | 缓解措施 |
|--------|--------|------|----------|
| PyQt6 API 不熟悉 | 高 | 中 | 提前学习文档，参考示例代码 |
| 打包体积过大 | 高 | 低 | 可以接受，或后续优化 |
| macOS权限限制 | 中 | 高 | 提前申请权限，提供用户指引 |
| 性能不达标 | 低 | 中 | 做好性能测试，优化关键路径 |
| 跨版本兼容性 | 中 | 中 | 测试多个macOS版本 |

### 应对方案

1. **学习计划：** 预留2-3天学习PyQt6
2. **最小化依赖：** 只打包必要的模块
3. **权限说明：** 在文档中说明权限需求
4. **性能监控：** 集成性能监控工具
5. **兼容性测试：** 在macOS 10.15+测试

---

## 🎯 里程碑

### M1: 基础框架完成（Day 3）
- ✅ 项目结构创建
- ✅ 基本UI显示
- ✅ 代码迁移完成

### M2: 核心功能完成（Day 10）
- ✅ 会话列表显示
- ✅ TodoWrite展示
- ✅ 实时更新工作

### M3: 功能完整（Day 17）
- ✅ 设置面板
- ✅ 通知系统
- ✅ 数据持久化

### M4: 可发布版本（Day 24）
- ✅ 优化完成
- ✅ 测试通过
- ✅ 应用打包
- ✅ 文档齐全

---

## 📝 总结

### 选择 PyQt6 的理由

1. **技术成熟：** PyQt6 是成熟的跨平台框架
2. **代码复用：** 90% 现有代码可直接使用
3. **开发效率：** 3-4周可完成开发
4. **性能优秀：** 原生体验，资源占用低
5. **可扩展性：** 未来可轻松跨平台

### 核心价值

- 🎯 **更低的使用门槛** - 图形界面更直观
- 📊 **更好的可见性** - 菜单栏常驻，随时查看
- 🔔 **更主动的通知** - 不错过重要信息
- ⚙️ **更灵活的配置** - 图形化设置界面

### 下一步

1. ✅ **技术方案确认** - 使用PyQt6
2. ⏭️ **环境搭建** - 创建项目骨架
3. ⏭️ **MVP开发** - 实现最小可行产品
4. ⏭️ **迭代优化** - 持续改进
5. ⏭️ **正式发布** - 内部推广使用

---

**更新记录：**
- v1.0 (2025-11-17): 初始方案
- v2.0 (2025-11-17): 确认PyQt6方案，添加详细技术设计

**联系方式：**
- 作者：哈雅
- 工号：263321
- 测试账号ID：2215135370526
