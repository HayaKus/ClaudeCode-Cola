"""
Claude Code Manager 主入口
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.ui.interface import UserInterface
from src.ui.assistant import Assistant
from src.core.session_manager import SessionManager
from src.core.notification import NotificationManager
from src.core.config import ConfigManager


class ClaudeCodeManager:
    """主应用类"""

    def __init__(self):
        """初始化管理器"""
        self.config_manager = ConfigManager()
        self.session_manager = SessionManager()
        self.notification_manager = NotificationManager(self.config_manager)
        self.ui = UserInterface()
        self.assistant = Assistant(self.session_manager)

    async def run(self):
        """运行主程序"""
        # 启动后台任务
        notification_task = asyncio.create_task(self._notification_loop())
        refresh_task = asyncio.create_task(self._refresh_loop())

        try:
            # 运行 UI
            await self.ui.run()
        finally:
            # 取消后台任务
            notification_task.cancel()
            refresh_task.cancel()

            try:
                await notification_task
                await refresh_task
            except asyncio.CancelledError:
                pass

    async def _notification_loop(self):
        """通知检查循环"""
        while True:
            try:
                # 刷新会话状态
                self.session_manager.refresh_sessions()

                # 检查并发送通知
                sessions = self.session_manager.get_active_sessions()
                self.notification_manager.check_and_notify(sessions)

                # 每30秒检查一次
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"通知循环出错: {e}")
                await asyncio.sleep(30)

    async def _refresh_loop(self):
        """会话刷新循环"""
        while True:
            try:
                # 刷新会话状态
                self.session_manager.refresh_sessions()

                # 每5秒刷新一次
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"刷新循环出错: {e}")
                await asyncio.sleep(5)


def main():
    """主函数"""
    try:
        # 创建应用实例
        app = ClaudeCodeManager()

        # 运行应用
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"程序错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()