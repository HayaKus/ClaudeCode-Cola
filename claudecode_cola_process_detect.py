#!/usr/bin/env python3
"""
ClaudeCode-Cola 🥤 - 让你的Claude Code会话像可乐一样清爽
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


# 白色背景主题配色
THEME = {
    "header_bg": "dark_blue",
    "header_text": "bold white on dark_blue",
    "primary": "bold dark_blue",
    "success": "bold dark_green",
    "warning": "bold dark_orange",
    "error": "bold dark_red",
    "info": "bold dark_cyan",
    "text": "bold black",
    "text_secondary": "gray50",
    "panel_border": "dark_blue",
}


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
    process_pid: Optional[int] = None  # 关联的Claude进程PID

    @property
    def duration(self) -> str:
        """计算会话持续时间"""
        delta = self.last_activity - self.start_time
        total_seconds = delta.total_seconds()

        # 处理负数时长（可能是时区问题或文件时间戳问题）
        if total_seconds < 0:
            # 如果时长为负，使用最后活动时间到现在的时长
            delta = datetime.now() - self.last_activity
            total_seconds = delta.total_seconds()

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)

        # 如果仍然为负或为0，显示为0
        if hours < 0 or (hours == 0 and minutes == 0):
            return "0h 0m"

        return f"{hours}h {minutes}m"

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
        self.console.print(f"[{THEME['primary']}]🥤 启动 ClaudeCode-Cola...[/]")

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
        self.console.print(f"[{THEME['warning']}]📂 扫描现有会话文件...[/]")

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

        self.console.print(f"[{THEME['success']}]✓ 扫描完成，找到 {session_count} 个会话[/]")

    async def parse_session(self, file_path: Path) -> Optional[ClaudeSession]:
        """解析单个会话文件"""
        try:
            session_id = file_path.stem
            project_path = file_path.parent.name
            # 处理项目路径
            # Claude Code 使用特殊的路径编码格式
            project_name = project_path

            # 处理特殊的路径编码
            # 例如: "-Users-haya-Code-ClaudeCode-Cola" -> "Code/ClaudeCode-Cola"
            # 例如: "-Users-haya-Desktop" -> "Desktop"
            # 例如: "-Users-haya-Code-claude-code-manager" -> "Code/claude-code-manager"

            # 移除前导的 - 符号
            if project_name.startswith('-'):
                project_name = project_name[1:]

            # 移除 Users-haya- 前缀
            if project_name.startswith('Users-haya-'):
                project_name = project_name[11:]

            # 智能处理路径分隔
            # 只将路径分隔符的横线替换为斜线，保留项目名中的横线
            # 识别常见的目录名，这些后面的第一个横线是路径分隔符
            common_dirs = ['Code', 'Desktop', 'Documents', 'Downloads', 'Projects', 'Library', 'Applications']
            for dir_name in common_dirs:
                if project_name.startswith(dir_name + '-'):
                    # 只替换目录名后的第一个横线为斜线
                    project_name = dir_name + '/' + project_name[len(dir_name) + 1:]
                    break

            # 如果没有匹配到常见目录，但包含横线，可能是简单路径
            # 例如: "Desktop" 保持不变
            # 这种情况下不做任何处理

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

            # 初始扫描时不设置活跃状态，等待进程检测来确定
            session.is_active = False

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
                            new_todos = []
                            for todo in todos_data:
                                timestamp_str = data.get('timestamp', datetime.now().isoformat()).replace('Z', '+00:00')
                                timestamp = datetime.fromisoformat(timestamp_str)
                                # 如果有时区信息，转换为本地时间
                                if timestamp.tzinfo:
                                    timestamp = timestamp.replace(tzinfo=None)

                                new_todos.append(TodoItem(
                                    content=todo.get('content', ''),
                                    status=todo.get('status', 'pending'),
                                    activeForm=todo.get('activeForm', ''),
                                    timestamp=timestamp
                                ))
                            session.todos = new_todos

                # 更新时间戳
                if 'timestamp' in data:
                    try:
                        # 统一转换为不带时区的本地时间
                        timestamp_str = data['timestamp'].replace('Z', '+00:00')
                        timestamp = datetime.fromisoformat(timestamp_str)
                        # 如果有时区信息，转换为本地时间
                        if timestamp.tzinfo:
                            timestamp = timestamp.replace(tzinfo=None)
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

                    # 更新活动时间，但不改变活跃状态（由进程检测决定）
                    session.last_activity = datetime.now()

        except Exception as e:
            pass

    async def handle_new_session(self, file_path: str):
        """处理新会话创建"""
        session = await self.parse_session(Path(file_path))
        if session:
            self.sessions[session.session_id] = session
            self.console.print(f"[{THEME['success']}]🆕 发现新会话: {session.project_name}[/]")

    def start_file_watcher(self):
        """启动文件系统监控"""
        event_handler = JSONLWatcher(self)
        # 设置当前事件循环
        event_handler.loop = asyncio.get_event_loop()
        self.observer.schedule(event_handler, str(self.claude_root), recursive=True)
        self.observer.start()
        self.console.print(f"[{THEME['success']}]👁️  文件监控已启动[/]")

    async def monitor_processes(self):
        """监控Claude进程"""
        while self.running:
            try:
                # 查找Claude进程并获取工作目录
                claude_process_info = {}
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                    try:
                        if 'claude' in proc.info['name'].lower():
                            pid = proc.info['pid']
                            # 获取进程工作目录
                            try:
                                cwd = proc.cwd()
                                claude_process_info[pid] = cwd
                            except:
                                pass
                    except:
                        continue

                # 更新进程列表
                self.claude_processes = list(claude_process_info.keys())

                # 匹配进程到会话
                await self.match_processes_to_sessions(claude_process_info)

                # 每2秒检查一次，以便快速检测进程变化
                await asyncio.sleep(2)

            except Exception:
                await asyncio.sleep(2)

    async def match_processes_to_sessions(self, claude_process_info: Dict[int, str]):
        """匹配Claude进程到对应的会话"""
        # 首先，重置所有会话的进程PID
        for session in self.sessions.values():
            session.process_pid = None

        # 匹配进程到会话
        for pid, cwd in claude_process_info.items():
            # 标准化工作目录路径
            cwd_normalized = cwd.replace('/', '-')
            if cwd_normalized.startswith('/'):
                cwd_normalized = cwd_normalized[1:]

            # 查找匹配的会话
            for session in self.sessions.values():
                # 检查项目路径是否匹配
                if cwd_normalized.endswith(session.project_path):
                    session.process_pid = pid
                    session.is_active = True
                    self.active_sessions.add(session.session_id)
                    break

        # 立即将没有进程的会话标记为非活跃
        for session in self.sessions.values():
            if session.process_pid is None and session.is_active:
                # 只有之前是活跃的，现在没有进程了，才立即标记为非活跃
                session.is_active = False
                self.active_sessions.discard(session.session_id)
                self.console.print(f"[{THEME['warning']}]💤 会话已关闭: {session.project_name}[/]")

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
        header_text = Text("🥤 ClaudeCode-Cola", style=THEME['header_text'], justify="center")
        layout["header"].update(Panel(header_text, style=THEME['header_bg']))

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
            f"[{THEME['info']}]总会话数[/]\n[{THEME['text']}]{total_sessions}[/]",
            f"[{THEME['success']}]活跃会话[/]\n[{THEME['text']}]{active_sessions}[/]",
            f"[{THEME['warning']}]TodoWrite项目[/]\n[{THEME['text']}]{todo_projects}[/]",
            f"[{THEME['error']}]待完成任务[/]\n[{THEME['text']}]{pending_todos}[/]"
        )

        layout["stats"].update(Panel(stats_table, title="📊 概览统计", style=THEME['info']))

        # 主内容区域 - 使用垂直布局
        main_layout = Layout()
        main_layout.split_column(
            Layout(name="sessions", ratio=3),  # 会话列表占主要空间
            Layout(name="todos", size=10)  # TodoWrite 固定高度
        )

        # 会话列表
        sessions_table = self.create_sessions_table()
        main_layout["sessions"].update(Panel(sessions_table, title="💻 会话列表", style=THEME['success']))

        # TodoWrite汇总
        todos_panel = self.create_todos_panel()
        main_layout["todos"].update(Panel(todos_panel, title="📝 TodoWrite 汇总", style=THEME['warning']))

        layout["main"].update(main_layout)

        # 页脚
        footer_text = Text(
            f"进程: {len(self.claude_processes)} | 按 Ctrl+C 退出 | 更新时间: {datetime.now().strftime('%H:%M:%S')}",
            style=THEME['primary'],
            justify="center"
        )
        layout["footer"].update(Panel(footer_text, style=THEME['primary']))

        return layout

    def create_sessions_table(self) -> Table:
        """创建会话列表表格"""
        table = Table(
            show_header=True,
            header_style=THEME['primary'],
            expand=True,  # 自动扩展以填充可用空间
            box=None,  # 移除边框以节省空间
            padding=(0, 1),  # 减少单元格内边距
            caption=None  # 移除误导性提示
        )
        table.add_column("", width=2, no_wrap=True)  # 状态图标
        table.add_column("项目", min_width=40, max_width=60, overflow="ellipsis")
        table.add_column("会话ID", width=36, no_wrap=True)  # 显示完整UUID
        table.add_column("TodoWrite进度", min_width=30, max_width=40, overflow="ellipsis")
        table.add_column("更新时间", width=15, no_wrap=True)

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

            # 处理项目名显示
            project_name = session.project_name
            if len(project_name) > 25:
                # 如果项目名太长，显示路径的最后部分
                parts = project_name.split('/')
                if len(parts) > 1:
                    project_name = f".../{parts[-1]}"
                else:
                    project_name = project_name[:22] + "..."

            table.add_row(
                status_icon,
                Text(project_name, style=THEME['text'] if session.is_active else THEME['text_secondary']),
                session.session_id,  # 显示完整的session_id
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
        table.add_row(Text(stats_text, style=THEME['text']))
        table.add_row("")  # 空行

        # 显示最近的任务
        table.add_row(Text("最新任务:", style=THEME['info']))
        for session, todo in all_todos[:10]:
            project = session.project_name.split('/')[-1]
            text = f"{todo.status_icon} [{project}] {todo.content}"
            style = THEME['success'] if todo.status == "completed" else THEME['warning'] if todo.status == "in_progress" else THEME['text_secondary']
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

                    # 活跃状态完全由进程检测决定，不再基于时间判断

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