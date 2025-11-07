"""
用户界面模块
"""
import asyncio
from datetime import datetime
from typing import List, Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.align import Align
from rich import box

from ..core.models import Session, SessionStatus
from ..core.session_manager import SessionManager
from ..core.iterm2_integration import ITerm2Integration
from ..core.config import ConfigManager


class UserInterface:
    """用户界面类"""

    def __init__(self):
        """初始化用户界面"""
        self.console = Console()
        self.session_manager = SessionManager()
        self.iterm2 = ITerm2Integration()
        self.config_manager = ConfigManager()
        self.running = True
        self.auto_refresh = True
        self.refresh_interval = 5
        self.assistant_callback: Optional[Callable] = None

    def create_layout(self) -> Layout:
        """创建界面布局"""
        layout = Layout(name="root")

        # 分割布局
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=4)
        )

        # body 分为左右两部分
        layout["body"].split_row(
            Layout(name="sessions", ratio=3),
            Layout(name="assistant", ratio=1)
        )

        return layout

    def render_header(self) -> Panel:
        """渲染头部"""
        title = Text("Claude Code Manager v1.0 - 你的智能会话管家", style="bold white")
        subtitle = Text("像可口可乐一样让你的编程体验充满活力！", style="italic cyan")

        content = Align.center(title + "\n" + subtitle)

        return Panel(
            content,
            style="bold blue",
            border_style="bright_blue",
            box=box.DOUBLE
        )

    def render_sessions(self) -> Panel:
        """渲染会话列表"""
        # 创建表格
        table = Table(show_header=True, header_style="bold magenta", expand=True)

        # 添加列
        table.add_column("", width=3)  # 状态图标
        table.add_column("ID", style="dim", width=8)
        table.add_column("名称", style="cyan", width=25)
        table.add_column("目录", style="green", width=30)
        table.add_column("时长", width=10)
        table.add_column("状态", width=20)
        table.add_column("进度", width=15)

        # 获取活跃会话
        active_sessions = self.session_manager.get_active_sessions()

        # 添加活跃会话
        if active_sessions:
            table.add_row("[bold green]🟢 活跃会话[/bold green]", "", "", "", "", "", "")
            table.add_row("", "", "", "", "", "", "")  # 空行

            for i, session in enumerate(active_sessions, 1):
                status_icon = self._get_status_icon(session)
                session_name = f"{'⭐ ' if session.is_starred else ''}{session.name}"

                # 计算运行时长
                duration = datetime.now() - session.created_at
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                duration_str = f"{hours}h {minutes}m"

                # 状态信息
                status_info = self._get_status_info(session)

                # 进度信息
                progress = ""
                if session.todo_progress:
                    percentage = session.todo_progress.percentage
                    progress = f"{session.todo_progress.completed}/{session.todo_progress.total} ({percentage:.0f}%)"
                    if percentage == 100:
                        progress += " ✅"

                table.add_row(
                    f"[{i}]",
                    session.id[:6],
                    session_name,
                    session.work_dir,
                    duration_str,
                    status_info,
                    progress
                )

        # 添加最近关闭的会话
        closed_sessions = self.session_manager.get_closed_sessions(hours=24)
        if closed_sessions:
            table.add_row("", "", "", "", "", "", "")  # 空行
            table.add_row("[bold red]🔴 最近关闭[/bold red]", "", "", "", "", "", "")
            table.add_row("", "", "", "", "", "", "")  # 空行

            for i, session in enumerate(closed_sessions[:5], len(active_sessions) + 1):
                closed_time = ""
                if session.closed_at:
                    time_diff = datetime.now() - session.closed_at
                    hours = int(time_diff.total_seconds() // 3600)
                    if hours < 1:
                        minutes = int(time_diff.total_seconds() // 60)
                        closed_time = f"{minutes}分钟前"
                    else:
                        closed_time = f"{hours}小时前"

                table.add_row(
                    f"[{i}]",
                    session.id[:6],
                    session.name,
                    session.work_dir,
                    session.duration or "",
                    closed_time,
                    f"{session.todo_progress.percentage:.0f}%" if session.todo_progress else ""
                )

        return Panel(
            table,
            title="会话列表",
            border_style="bright_blue"
        )

    def render_assistant(self, messages: List[str]) -> Panel:
        """渲染助手面板"""
        # 显示最近的消息
        content = "\n".join(messages[-10:]) if messages else "我是你的会话管家，有什么可以帮助你的吗？"

        return Panel(
            content,
            title="AI 助手",
            border_style="bright_green"
        )

    def render_footer(self) -> Panel:
        """渲染底部输入区"""
        help_text = "[bold cyan]快捷键:[/bold cyan] "
        help_text += "[N]新建 [R]恢复 [T]模板 [S]设置 [H]帮助 [Q]退出"

        return Panel(
            help_text,
            border_style="dim"
        )

    def _get_status_icon(self, session: Session) -> str:
        """获取会话状态图标"""
        if session.performance:
            # 检查异常状态
            if session.performance.cpu_percent > self.config_manager.config.performance.high_cpu_threshold:
                return "🔥"  # 高资源占用
            if session.performance.inactive_minutes > self.config_manager.config.performance.inactive_threshold_minutes:
                return "⚠️"  # 长时间未活动

        if session.status == SessionStatus.CRASHED:
            return "🔴"  # 异常退出
        elif session.status == SessionStatus.PAUSED:
            return "⏸️"  # 暂停
        elif session.status == SessionStatus.RUNNING:
            return "🟢"  # 运行中
        else:
            return "⚪"  # 已停止

    def _get_status_info(self, session: Session) -> str:
        """获取会话状态信息"""
        status_parts = []

        if session.performance:
            status_parts.append(f"CPU: {session.performance.cpu_percent:.1f}%")
            status_parts.append(f"MEM: {session.performance.memory_mb:.0f}MB")

            if session.performance.inactive_minutes > 0:
                status_parts.append(f"闲置 {session.performance.inactive_minutes}分钟")

        return " | ".join(status_parts) if status_parts else "运行中"

    async def show_main_menu(self) -> None:
        """显示主菜单"""
        while self.running:
            choice = Prompt.ask(
                "\n选择操作",
                choices=["n", "r", "t", "s", "h", "q"],
                default="h"
            )

            if choice == "n":
                await self.create_new_session()
            elif choice == "r":
                await self.restore_session()
            elif choice == "t":
                await self.show_templates()
            elif choice == "s":
                await self.show_settings()
            elif choice == "h":
                self.show_help()
            elif choice == "q":
                if Confirm.ask("确定要退出吗？"):
                    self.running = False
                    break

    async def create_new_session(self) -> None:
        """创建新会话"""
        self.console.print("\n[bold cyan]创建新的 Claude Code 会话[/bold cyan]")

        # 输入会话名称
        name = Prompt.ask("会话名称")
        if not name:
            self.console.print("[red]会话名称不能为空[/red]")
            return

        # 输入工作目录
        default_dir = self.config_manager.config.general.default_work_dir
        work_dir = Prompt.ask("工作目录", default=default_dir)

        # 选择标签
        tags = []
        tag_choices = ["API开发", "Bug修复", "文档", "测试", "重构", "其他"]
        self.console.print("\n选择标签（多选，用空格分隔）：")
        for i, tag in enumerate(tag_choices, 1):
            self.console.print(f"  [{i}] {tag}")

        tag_input = Prompt.ask("选择标签", default="")
        if tag_input:
            selected_indices = [int(x.strip()) for x in tag_input.split() if x.strip().isdigit()]
            tags = [tag_choices[i-1] for i in selected_indices if 0 < i <= len(tag_choices)]

        # 创建会话
        session = self.session_manager.create_session(name, work_dir, tags)

        # 在 iTerm2 中启动
        success = self.iterm2.create_new_window(session.name, session.id, session.work_dir)

        if success:
            self.console.print(f"[green]✅ 会话 '{session.name}' 创建成功！[/green]")
        else:
            self.console.print(f"[red]❌ 创建会话失败[/red]")

    async def restore_session(self) -> None:
        """恢复会话"""
        closed_sessions = self.session_manager.get_closed_sessions()

        if not closed_sessions:
            self.console.print("[yellow]没有可恢复的会话[/yellow]")
            return

        self.console.print("\n[bold cyan]选择要恢复的会话：[/bold cyan]")

        # 显示会话列表
        for i, session in enumerate(closed_sessions, 1):
            self.console.print(
                f"  [{i}] {session.name} - {session.work_dir} "
                f"(关闭于 {session.closed_at.strftime('%Y-%m-%d %H:%M')})"
            )

        # 选择会话
        choice = Prompt.ask("选择会话编号", default="1")
        try:
            index = int(choice) - 1
            if 0 <= index < len(closed_sessions):
                session = closed_sessions[index]

                # 恢复会话
                success = self.iterm2.restore_session(
                    session.id,
                    session.name,
                    session.work_dir
                )

                if success:
                    self.console.print(f"[green]✅ 会话 '{session.name}' 恢复成功！[/green]")
                    # 更新会话状态
                    # 这里需要实现将会话从已关闭移到活跃
                else:
                    self.console.print(f"[red]❌ 恢复会话失败[/red]")
            else:
                self.console.print("[red]无效的选择[/red]")
        except ValueError:
            self.console.print("[red]请输入有效的数字[/red]")

    async def show_templates(self) -> None:
        """显示模板列表"""
        templates = self.session_manager.get_templates()

        self.console.print("\n[bold cyan]会话模板：[/bold cyan]")

        for i, template in enumerate(templates, 1):
            self.console.print(f"\n[{i}] [bold]{template.name}[/bold]")
            self.console.print(f"    目录: {template.work_dir}")
            self.console.print(f"    名称模式: {template.name_pattern}")
            self.console.print(f"    标签: {', '.join(template.tags)}")
            if template.default_todos:
                self.console.print(f"    默认任务: {len(template.default_todos)}个")

        # TODO: 实现使用模板创建会话的功能

    async def show_settings(self) -> None:
        """显示设置界面"""
        self.console.print("\n[bold cyan]设置[/bold cyan]")
        self.console.print("功能开发中...")
        # TODO: 实现设置界面

    def show_help(self) -> None:
        """显示帮助信息"""
        help_text = """
[bold cyan]Claude Code Manager 帮助[/bold cyan]

[bold]快捷键：[/bold]
  N - 创建新会话
  R - 恢复已关闭的会话
  T - 查看/使用模板
  S - 打开设置
  H - 显示此帮助
  Q - 退出程序

[bold]功能说明：[/bold]
  • 自动监控所有 Claude Code 会话
  • 实时显示会话状态和性能信息
  • 支持会话的创建、恢复和管理
  • 集成 AI 助手提供智能建议

[bold]更多信息：[/bold]
  访问 https://github.com/yourusername/ClaudeCode-Cola
        """
        self.console.print(help_text)

    async def run(self) -> None:
        """运行用户界面"""
        # 检查 iTerm2
        if not self.iterm2.is_iterm2_running():
            self.console.print("[red]错误：iTerm2 未运行，请先启动 iTerm2[/red]")
            return

        # 显示欢迎信息
        self.console.print(self.render_header())

        # 主循环
        try:
            layout = self.create_layout()
            messages = []

            with Live(layout, refresh_per_second=1) as live:
                # 更新布局
                layout["header"].update(self.render_header())

                # 启动自动刷新任务
                refresh_task = asyncio.create_task(self.auto_refresh_sessions(layout, messages))

                # 显示主菜单
                await self.show_main_menu()

                # 取消刷新任务
                refresh_task.cancel()

        except KeyboardInterrupt:
            self.console.print("\n[yellow]程序被中断[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]发生错误：{e}[/red]")

    async def auto_refresh_sessions(self, layout: Layout, messages: List[str]) -> None:
        """自动刷新会话列表"""
        while self.running and self.auto_refresh:
            try:
                # 刷新会话状态
                self.session_manager.refresh_sessions()

                # 更新界面
                layout["sessions"].update(self.render_sessions())
                layout["assistant"].update(self.render_assistant(messages))
                layout["footer"].update(self.render_footer())

                # 等待下次刷新
                await asyncio.sleep(self.refresh_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.console.print(f"[red]刷新时出错：{e}[/red]")
                await asyncio.sleep(self.refresh_interval)