"""
ClaudeCode-Cola 主应用类
"""
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import QTimer, Qt

from src.ui.main_window import MainWindow
from src.ui.system_tray import SystemTray
from src.core.multi_source_monitor import MultiSourceMonitor
from src.data.config import Config
from src.utils.logger import logger
from PyQt6.QtGui import QShortcut, QKeySequence


class ColaApp:
    """ClaudeCode-Cola 主应用"""

    def __init__(self):
        """初始化应用"""
        logger.info("初始化 ClaudeCode-Cola 应用...")

        # 加载配置
        self.config = Config()

        # 创建主窗口
        self.main_window = MainWindow(config=self.config)

        # 创建系统托盘
        self.system_tray = SystemTray(parent=self.main_window)

        # 创建会话监控器（多源：Claude Code + Qoder）
        self.session_monitor = MultiSourceMonitor()

        # 设置连接
        self.setup_connections()

        # 启动监控器
        self.session_monitor.start()

        # 设置定时刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.on_timer_refresh)
        self.refresh_timer.start(self.config.refresh_interval * 1000)  # 转换为毫秒

        logger.info("✅ 应用初始化完成")

    def setup_connections(self):
        """设置信号连接"""
        # 系统托盘信号
        self.system_tray.show_window_requested.connect(self.show_main_window)
        self.system_tray.refresh_requested.connect(self.on_refresh)
        self.system_tray.quit_requested.connect(self.quit)

        # 主窗口信号
        self.main_window.refresh_requested.connect(self.on_refresh)
        self.main_window.pin_toggled.connect(self.on_pin_toggled)
        self.main_window.session_renamed.connect(self.on_session_renamed)

        # 会话监控器信号
        self.session_monitor.sessions_updated.connect(self.on_sessions_updated)

    def show(self):
        """显示应用"""
        # 显示系统托盘
        self.system_tray.show()

        # 根据配置决定是否显示主窗口
        if self.config.show_window_on_start:
            self.show_main_window()

    def show_main_window(self):
        """显示主窗口"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def on_refresh(self):
        """刷新数据"""
        logger.info("手动刷新数据...")
        self.session_monitor.scan_all_sessions()

    def on_timer_refresh(self):
        """定时刷新"""
        if self.config.auto_refresh:
            logger.info("🔄 自动刷新数据...")
            self.session_monitor.scan_all_sessions()

    def on_sessions_updated(self, sessions):
        """会话数据更新"""
        # 更新主窗口
        self.main_window.update_sessions(sessions)

        # 计算需要关注的会话数（被标记且不活跃）
        need_attention_count = sum(1 for s in sessions if s.is_pinned and not s.is_active)
        total_count = len(sessions)
        
        # 更新系统托盘
        self.system_tray.update_status(total_count, need_attention_count)

        # 更新托盘菜单和弹出窗口（传递所有会话，让它们自己过滤）
        self.system_tray.update_active_sessions_menu(sessions)

    def on_pin_toggled(self, session_id: str, pin: bool):
        """处理标记/取消标记会话"""
        import json
        from pathlib import Path
        
        # 配置文件路径
        config_dir = Path.home() / '.claudecode-cola'
        config_file = config_dir / 'pinned_sessions.json'
        
        # 确保配置目录存在
        config_dir.mkdir(exist_ok=True)
        
        # 加载已标记的会话列表
        pinned_sessions = set()
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    pinned_sessions = set(json.load(f))
            except:
                pass
        
        # 更新标记状态
        if pin:
            pinned_sessions.add(session_id)
            logger.info(f"✅ 会话 {session_id} 已标记")
        else:
            if session_id in pinned_sessions:
                pinned_sessions.remove(session_id)
                logger.info(f"📌 会话 {session_id} 已取消标记")
        
        # 保存到配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(list(pinned_sessions), f, ensure_ascii=False, indent=2)
        
        # 重新加载标记的会话列表到所有监控器
        self.session_monitor.claude_monitor.load_pinned_sessions()
        self.session_monitor.qoder_monitor.load_pinned_sessions()

        # 刷新会话列表
        self.session_monitor.scan_all_sessions()

    def on_session_renamed(self, session_id: str, new_name: str):
        """处理会话重命名"""
        import json
        from pathlib import Path
        
        # 配置文件路径
        config_dir = Path.home() / '.claudecode-cola'
        config_file = config_dir / 'session_names.json'
        
        # 确保配置目录存在
        config_dir.mkdir(exist_ok=True)
        
        # 加载已有的自定义名称
        session_names = {}
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    session_names = json.load(f)
            except:
                pass
        
        # 更新名称
        if new_name:
            session_names[session_id] = new_name
            logger.info(f"✏️ 会话 {session_id} 重命名为: {new_name}")
        else:
            # 如果新名称为空，删除自定义名称
            if session_id in session_names:
                del session_names[session_id]
                logger.info(f"🗑️ 会话 {session_id} 的自定义名称已删除")
        
        # 保存到配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(session_names, f, ensure_ascii=False, indent=2)
        
        # 重新加载自定义名称到所有监控器
        self.session_monitor.claude_monitor.load_session_names()
        self.session_monitor.qoder_monitor.load_session_names()

        # 刷新会话列表
        self.session_monitor.scan_all_sessions()

    def quit(self):
        """退出应用"""
        logger.info("正在退出应用...")
        
        # 先断开所有信号连接，避免在退出过程中触发更新
        try:
            self.session_monitor.sessions_updated.disconnect()
        except:
            pass
        
        # 停止会话监控器
        self.session_monitor.stop()
        
        # 停止定时器
        self.refresh_timer.stop()
        
        # 强制关闭主窗口
        self.main_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.main_window.close()
        
        # 退出应用
        from PyQt6.QtWidgets import QApplication
        logger.info("👋 应用即将退出")
        QApplication.quit()
