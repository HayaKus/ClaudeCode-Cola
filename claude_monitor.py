#!/usr/bin/env python3
"""
Claude Code Monitor - 监控所有Claude Code会话和TodoWrite状态
作者: 哈雅
"""

import os
import json
import asyncio
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import aiofiles
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
import time


@dataclass
class TodoItem:
    """TodoWrite中的单个任务项"""
    content: str
    status: str  # pending, in_progress, completed
    activeForm: str
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def status_icon(self) -> str:
        """返回状态对应的图标"""
        icons = {
            'completed': '✅',
            'in_progress': '🔄',
            'pending': '⏳'
        }
        return icons.get(self.status, '❓')


@dataclass
class ClaudeSession:
    """Claude Code会话信息"""
    session_id: str
    project_path: str
    project_name: str
    start_time: datetime
    last_activity: datetime
    is_active: bool = False
    todos: List[TodoItem] = field(default_factory=list)
    message_count: int = 0
    last_message: str = ""
    file_path: str = ""

    @property
    def duration(self) -> str:
        """计算会话持续时间"""
        delta = self.last_activity - self.start_time
        hours = delta.total_seconds() // 3600
        minutes = (delta.total_seconds() % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m"

    @property
    def todo_stats(self) -> Dict[str, int]:
        """统计TodoWrite任务状态"""
        stats = defaultdict(int)
        for todo in self.todos:
            stats[todo.status] += 1
        return dict(stats)

    @property
    def todo_progress(self) -> str:
        """返回任务进度字符串"""
        stats = self.todo_stats
        total = len(self.todos)
        if total == 0:
            return "无任务"
        completed = stats.get('completed', 0)
        return f"[{self.todos[-1].status_icon} {completed}/{total}] {self.todos[-1].content if self.todos else ''}"


class JSONLWatcher(FileSystemEventHandler):
    """文件系统监控器"""
    def __init__(self, monitor):
        self.monitor = monitor
        self.file_positions = {}
        self.loop = None

    def on_modified(self, event):
        """文件修改事件处理"""
        if event.src_path.endswith('.jsonl') and not event.is_directory:
            # 获取事件循环并创建任务
            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self.monitor.handle_file_update(event.src_path),
                    self.loop
                )

    def on_created(self, event):
        """文件创建事件处理"""
        if event.src_path.endswith('.jsonl') and not event.is_directory:
            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self.monitor.handle_new_session(event.src_path),
                    self.loop
                )


class ClaudeMonitor:
    """Claude Code全局监控器"""

    def __init__(self):
        self.sessions: Dict[str, ClaudeSession] = {}
        self.active_sessions: Set[str] = set()
        self.claude_processes = []
        self.console = Console()
        self.observer = Observer()
        self.file_positions = {}  # 记录每个文件的读取位置
        self.running = True

        # Claude项目根目录
        self.claude_root = Path.home() / '.claude' / 'projects'

    async def start(self):
        """启动监控器"""
        self.console.print("[bold green]🚀 启动Claude Code监控器...[/bold green]")

        # 扫描现有会话
        await self.scan_existing_sessions()

        # 启动文件监控
        self.start_file_watcher()

        # 启动进程监控
        asyncio.create_task(self.monitor_processes())

        # 启动UI
        await self.run_ui()

    async def scan_existing_sessions(self):
        """扫描所有现有的Claude会话"""
        self.console.print("[yellow]📂 扫描现有会话文件...[/yellow]")

        session_count = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("扫描中...", total=None)

            if self.claude_root.exists():
                for project_dir in self.claude_root.iterdir():
                    if project_dir.is_dir():
                        for jsonl_file in project_dir.glob('*.jsonl'):
                            session = await self.parse_session(jsonl_file)
                            if session:
                                self.sessions[session.session_id] = session
                                session_count += 1
                                progress.update(task, description=f"已扫描 {session_count} 个会话")

        self.console.print(f"[green]✓ 扫描完成，找到 {session_count} 个会话[/green]")

    async def parse_session(self, file_path: Path) -> Optional[ClaudeSession]:
        """解析单个会话文件"""
        try:
            session_id = file_path.stem
            project_path = file_path.parent.name
            project_name = project_path.replace('-Users-haya-', '').replace('-', '/')

            session = ClaudeSession(
                session_id=session_id,
                project_path=project_path,
                project_name=project_name,
                start_time=datetime.fromtimestamp(file_path.stat().st_ctime),
                last_activity=datetime.fromtimestamp(file_path.stat().st_mtime),
                file_path=str(file_path)
            )

            # 读取文件内容，提取TodoWrite和其他信息
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                lines = await f.readlines()
                self.file_positions[str(file_path)] = len(lines)

                for line in lines:
                    await self.parse_line(line, session)

            # 检查是否为活跃会话（最近30分钟内有活动）
            time_diff = (datetime.now() - session.last_activity).total_seconds()
            if time_diff < 1800:  # 30分钟
                session.is_active = True
                self.active_sessions.add(session_id)

            return session

        except Exception as e:
            # 静默处理错误，避免影响其他文件的解析
            return None

    async def parse_line(self, line: str, session: ClaudeSession) -> None:
        """解析JSONL行，提取关键信息"""
        try:
            data = json.loads(line.strip())

            # 更新消息计数
            if data.get('type') in ['user', 'assistant']:
                session.message_count += 1

                # 提取最后一条消息
                if data.get('type') == 'user':
                    message = data.get('message', {})
                    if isinstance(message.get('content'), str):
                        session.last_message = message['content'][:100]

                # 检查TodoWrite调用
                if data.get('type') == 'assistant':
                    message = data.get('message', {})
                    content = message.get('content', [])

                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'tool_use' and item.get('name') == 'TodoWrite':
                            todos_data = item.get('input', {}).get('todos', [])
                            # 更新整个todo列表
                            session.todos = [
                                TodoItem(
                                    content=todo.get('content', ''),
                                    status=todo.get('status', 'pending'),
                                    activeForm=todo.get('activeForm', ''),
                                    timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()).replace('Z', '+00:00'))
                                )
                                for todo in todos_data
                            ]

                # 更新时间戳
                if 'timestamp' in data:
                    try:
                        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                        session.last_activity = timestamp
                    except:
                        pass

        except json.JSONDecodeError:
            pass
        except Exception:
            pass

    async def handle_file_update(self, file_path: str):
        """处理文件更新事件"""
        try:
            # 从文件路径提取session_id
            path = Path(file_path)
            session_id = path.stem

            # 如果是新会话，先创建
            if session_id not in self.sessions:
                await self.handle_new_session(file_path)
                return

            # 读取新增的行
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                lines = await f.readlines()

                # 获取上次读取的位置
                last_position = self.file_positions.get(file_path, 0)
                new_lines = lines[last_position:]

                if new_lines:
                    self.file_positions[file_path] = len(lines)

                    # 解析新行
                    session = self.sessions[session_id]
                    for line in new_lines:
                        await self.parse_line(line, session)

                    # 更新活跃状态
                    session.is_active = True
                    session.last_activity = datetime.now()
                    self.active_sessions.add(session_id)

        except Exception as e:
            pass

    async def handle_new_session(self, file_path: str):
        """处理新会话创建"""
        session = await self.parse_session(Path(file_path))
        if session:
            self.sessions[session.session_id] = session
            self.console.print(f"[green]🆕 发现新会话: {session.project_name}[/green]")

    def start_file_watcher(self):
        """启动文件系统监控"""
        event_handler = JSONLWatcher(self)
        # 设置当前事件循环
        event_handler.loop = asyncio.get_event_loop()
        self.observer.schedule(event_handler, str(self.claude_root), recursive=True)
        self.observer.start()
        self.console.print("[green]👁️  文件监控已启动[/green]")

    async def monitor_processes(self):
        """监控Claude进程"""
        while self.running:
            try:
                # 查找Claude进程
                claude_pids = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if 'claude' in proc.info['name'].lower():
                            claude_pids.append(proc.info['pid'])
                    except:
                        continue

                self.claude_processes = claude_pids

                # 每10秒检查一次
                await asyncio.sleep(10)

            except Exception:
                await asyncio.sleep(10)

    def create_dashboard(self) -> Layout:
        """创建仪表板布局"""
        layout = Layout()

        # 分割布局
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="stats", size=5),
            Layout(name="main", size=30),
            Layout(name="footer", size=3)
        )

        # 标题
        header_text = Text("🔍 Claude Code 全局监控中心", style="bold white on blue", justify="center")
        layout["header"].update(Panel(header_text, style="blue"))

        # 统计信息
        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column(justify="center")
        stats_table.add_column(justify="center")
        stats_table.add_column(justify="center")
        stats_table.add_column(justify="center")

        # 计算统计数据
        total_sessions = len(self.sessions)
        active_sessions = len(self.active_sessions)
        todo_projects = sum(1 for s in self.sessions.values() if s.todos)
        pending_todos = sum(
            sum(1 for t in s.todos if t.status == 'pending')
            for s in self.sessions.values()
        )

        stats_table.add_row(
            f"[cyan]总会话数[/cyan]\n[bold]{total_sessions}[/bold]",
            f"[green]活跃会话[/green]\n[bold]{active_sessions}[/bold]",
            f"[yellow]TodoWrite项目[/yellow]\n[bold]{todo_projects}[/bold]",
            f"[red]待完成任务[/red]\n[bold]{pending_todos}[/bold]"
        )

        layout["stats"].update(Panel(stats_table, title="📊 概览统计", style="cyan"))

        # 主内容区域
        main_layout = Layout()
        main_layout.split_row(
            Layout(name="sessions", ratio=3),
            Layout(name="todos", ratio=2)
        )

        # 会话列表
        sessions_table = self.create_sessions_table()
        main_layout["sessions"].update(Panel(sessions_table, title="💻 会话列表", style="green"))

        # TodoWrite汇总
        todos_panel = self.create_todos_panel()
        main_layout["todos"].update(Panel(todos_panel, title="📝 TodoWrite 汇总", style="yellow"))

        layout["main"].update(main_layout)

        # 页脚
        footer_text = Text(
            f"进程: {len(self.claude_processes)} | 按 Ctrl+C 退出 | 更新时间: {datetime.now().strftime('%H:%M:%S')}",
            style="dim",
            justify="center"
        )
        layout["footer"].update(Panel(footer_text, style="dim"))

        return layout

    def create_sessions_table(self) -> Table:
        """创建会话列表表格"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("状态", width=4)
        table.add_column("项目", width=30)
        table.add_column("会话ID", width=12)
        table.add_column("时长", width=8)
        table.add_column("消息数", width=6)
        table.add_column("TodoWrite", width=40)
        table.add_column("最后活动", width=20)

        # 排序会话：活跃的在前，然后按最后活动时间
        sorted_sessions = sorted(
            self.sessions.values(),
            key=lambda s: (s.is_active, s.last_activity),
            reverse=True
        )

        # 只显示前20个会话
        for session in sorted_sessions[:20]:
            status_icon = "🟢" if session.is_active else "🔴"

            # TodoWrite进度
            if session.todos:
                todo_progress = session.todo_progress
            else:
                todo_progress = "无任务"

            table.add_row(
                status_icon,
                Text(session.project_name, style="bold" if session.is_active else "dim"),
                session.session_id[:8] + "...",
                session.duration,
                str(session.message_count),
                Text(todo_progress, overflow="ellipsis"),
                session.last_activity.strftime("%m-%d %H:%M:%S")
            )

        return table

    def create_todos_panel(self) -> Table:
        """创建TodoWrite汇总面板"""
        table = Table(show_header=False, box=None)
        table.add_column()

        # 统计所有TodoWrite
        all_todos = []
        for session in self.sessions.values():
            for todo in session.todos:
                all_todos.append((session, todo))

        # 按时间排序，显示最新的
        all_todos.sort(key=lambda x: x[1].timestamp, reverse=True)

        # 状态统计
        stats = defaultdict(int)
        for _, todo in all_todos:
            stats[todo.status] += 1

        # 添加统计行
        stats_text = f"✅ 已完成: {stats['completed']}  🔄 进行中: {stats['in_progress']}  ⏳ 待处理: {stats['pending']}"
        table.add_row(Text(stats_text, style="bold"))
        table.add_row("")  # 空行

        # 显示最近的任务
        table.add_row(Text("最新任务:", style="bold cyan"))
        for session, todo in all_todos[:10]:
            project = session.project_name.split('/')[-1]
            text = f"{todo.status_icon} [{project}] {todo.content}"
            style = "green" if todo.status == "completed" else "yellow" if todo.status == "in_progress" else "dim"
            table.add_row(Text(text, style=style, overflow="ellipsis"))

        return table

    async def run_ui(self):
        """运行UI循环"""
        with Live(
            self.create_dashboard(),
            refresh_per_second=2,
            console=self.console
        ) as live:
            try:
                while self.running:
                    # 更新UI
                    live.update(self.create_dashboard())

                    # 清理非活跃会话
                    current_time = datetime.now()
                    for session_id in list(self.active_sessions):
                        if session_id in self.sessions:
                            session = self.sessions[session_id]
                            if (current_time - session.last_activity).total_seconds() > 1800:
                                session.is_active = False
                                self.active_sessions.discard(session_id)

                    await asyncio.sleep(1)

            except KeyboardInterrupt:
                self.running = False
                raise

    def cleanup(self):
        """清理资源"""
        self.console.print("\n[yellow]🛑 正在停止监控器...[/yellow]")
        self.observer.stop()
        self.observer.join()
        self.console.print("[green]✅ 监控器已停止[/green]")


async def main():
    """主函数"""
    monitor = ClaudeMonitor()

    # 设置信号处理
    def signal_handler(sig, frame):
        monitor.running = False

    signal.signal(signal.SIGINT, signal_handler)

    try:
        await monitor.start()
    except KeyboardInterrupt:
        pass
    finally:
        monitor.cleanup()


if __name__ == "__main__":
    # 运行监控器
    asyncio.run(main())