#!/usr/bin/env python3
"""
ClaudeCode-Cola 🥤 - 让你的Claude Code会话像可乐一样清爽
作者: 哈雅

使用说明:
- 标记会话: python claudecode_cola_api.py pin <会话ID>
- 取消标记: python claudecode_cola_api.py unpin <会话ID>
- 查看标记列表: python claudecode_cola_api.py list
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
import threading
import sys
import select


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
    is_pinned: bool = False  # 是否被标记（固定显示）
    todos: List[TodoItem] = field(default_factory=list)
    message_count: int = 0
    last_message: str = ""
    file_path: str = ""

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
        self.input_queue = []  # 用于存储用户输入
        self.input_mode = False  # 是否处于输入模式
        self.input_buffer = ""  # 输入缓冲区
        self.status_message = ""  # 状态消息

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

        # 启动键盘输入监听
        self.start_input_listener()

        # 启动UI
        await self.run_ui()

    def load_pinned_sessions(self):
        """从配置文件加载已标记的会话"""
        from claudecode_cola_api import load_pinned_sessions
        try:
            pinned_session_ids = load_pinned_sessions()
            # 将已标记的状态同步到会话对象
            for session_id in pinned_session_ids:
                if session_id in self.sessions:
                    self.sessions[session_id].is_pinned = True
            return pinned_session_ids
        except:
            return set()

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

        # 加载已标记的会话状态
        self.load_pinned_sessions()

        self.console.print(f"[{THEME['success']}]✓ 扫描完成，找到 {session_count} 个会话[/]")

    async def parse_session(self, file_path: Path) -> Optional[ClaudeSession]:
        """解析单个会话文件"""
        try:
            session_id = file_path.stem
            # 过滤掉看起来不是真实会话的ID（如agent-开头的）
            if session_id.startswith('agent-'):
                return None
            project_path = file_path.parent.name
            # 处理项目路径 - 显示完整路径
            project_name = project_path

            # 将Claude的路径编码（使用-分隔符）转换为标准路径
            if project_name.startswith('-'):
                # 移除开头的'-'
                path_without_prefix = project_name[1:]
                # 将所有'-'替换为'/'来恢复路径
                project_name = '/' + path_without_prefix.replace('-', '/')

            # 过滤掉不完整的路径（如只有"/"这种）
            # 至少需要包括"/Users/haya"这样的2层路径
            if project_name.count('/') < 2:
                return None

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

            # 初始扫描时，检查文件最近是否有修改来确定是否活跃
            try:
                file_stat = Path(session.file_path).stat()
                file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
                time_diff = (datetime.now() - file_mtime).total_seconds()
                # 只有文件在最近2分钟内有修改才标记为活跃
                if time_diff < 120:  # 2分钟
                    session.is_active = True
                    self.active_sessions.add(session_id)
            except:
                # 如果无法获取文件状态，使用时间戳判断
                time_diff = (datetime.now() - session.last_activity).total_seconds()
                if time_diff < 120:  # 2分钟
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

                    # 更新活动时间，但不立即标记为活跃，等待UI循环中的文件修改时间检查来更新状态
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

    def start_input_listener(self):
        """启动键盘输入监听线程"""
        def input_thread():
            import termios
            import tty

            # 检查是否在终端环境中运行
            if not sys.stdin.isatty():
                self.console.print(f"[{THEME['warning']}]⚠️  非终端环境,键盘监听已禁用[/]")
                return

            try:
                # 保存原始终端设置
                old_settings = termios.tcgetattr(sys.stdin)
            except termios.error:
                self.console.print(f"[{THEME['warning']}]⚠️  无法访问终端,键盘监听已禁用[/]")
                return

            try:
                # 设置终端为原始模式
                tty.setcbreak(sys.stdin.fileno())

                while self.running:
                    # 检查是否有输入可用
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        # 读取第一个字符
                        char = sys.stdin.read(1)

                        # 如果还有更多字符可读(处理粘贴),继续读取
                        import fcntl
                        import os

                        # 设置为非阻塞模式临时读取剩余字符
                        fd = sys.stdin.fileno()
                        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

                        try:
                            while True:
                                try:
                                    next_char = sys.stdin.read(1)
                                    if next_char:
                                        char += next_char
                                    else:
                                        break
                                except IOError:
                                    break
                        finally:
                            # 恢复阻塞模式
                            fcntl.fcntl(fd, fcntl.F_SETFL, flags)

                        # 处理所有读取到的字符
                        for c in char:
                            if not self.input_mode:
                                # 非输入模式,检查是否是命令触发键
                                if c == 'p':
                                    self.input_mode = True
                                    self.input_buffer = "p "
                                    self.status_message = "输入会话ID进行标记 (按 Enter 确认, Esc 取消):"
                                elif c == 'u':
                                    self.input_mode = True
                                    self.input_buffer = "u "
                                    self.status_message = "输入会话ID取消标记 (按 Enter 确认, Esc 取消):"
                            else:
                                # 输入模式
                                if c == '\n' or c == '\r':
                                    # 确认输入
                                    self.process_input(self.input_buffer)
                                    self.input_mode = False
                                    self.input_buffer = ""
                                elif c == '\x1b':  # ESC键
                                    # 取消输入
                                    self.input_mode = False
                                    self.input_buffer = ""
                                    self.status_message = "已取消操作"
                                    self._status_message_time = time.time()
                                elif c == '\x7f':  # 退格键
                                    if len(self.input_buffer) > 2:  # 保留 "p " 或 "u "
                                        self.input_buffer = self.input_buffer[:-1]
                                elif c.isprintable():
                                    self.input_buffer += c
            finally:
                # 恢复终端设置
                try:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                except:
                    pass

        # 启动输入线程
        thread = threading.Thread(target=input_thread, daemon=True)
        thread.start()

        # 如果在终端环境,显示启动信息
        if sys.stdin.isatty():
            self.console.print(f"[{THEME['success']}]⌨️  键盘监听已启动[/]")

    def process_input(self, input_text):
        """处理用户输入"""
        from claudecode_cola_api import pin_session, unpin_session, save_pinned_sessions, load_pinned_sessions

        parts = input_text.strip().split()
        if len(parts) < 2:
            self.status_message = "❌ 输入格式错误"
            self._status_message_time = time.time()
            return

        command = parts[0]
        session_id = parts[1]

        if command == 'p':
            # 标记会话
            if session_id in self.sessions:
                session = self.sessions[session_id]
                if not session.is_pinned:
                    session.is_pinned = True
                    # 保存到配置文件
                    pinned_sessions = load_pinned_sessions()
                    pinned_sessions.add(session_id)
                    save_pinned_sessions(pinned_sessions)
                    self.status_message = f"✅ 已标记会话: {session.project_name}"
                else:
                    self.status_message = f"⚠️  会话已被标记: {session.project_name}"
            else:
                self.status_message = f"❌ 会话 {session_id} 不存在"

        elif command == 'u':
            # 取消标记会话
            if session_id in self.sessions:
                session = self.sessions[session_id]
                if session.is_pinned:
                    session.is_pinned = False
                    # 从配置文件移除
                    pinned_sessions = load_pinned_sessions()
                    pinned_sessions.discard(session_id)
                    save_pinned_sessions(pinned_sessions)
                    self.status_message = f"✅ 已取消标记会话: {session.project_name}"
                else:
                    self.status_message = f"⚠️  会话未被标记: {session.project_name}"
            else:
                self.status_message = f"❌ 会话 {session_id} 不存在"

        # 设置状态消息时间戳
        self._status_message_time = time.time()

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
        # 只统计活跃会话中的TodoWrite项目和任务
        active_sessions_list = [s for s in self.sessions.values() if s.is_active]
        todo_projects = sum(1 for s in active_sessions_list if s.todos)
        pending_todos = sum(
            sum(1 for t in s.todos if t.status == 'pending')
            for s in active_sessions_list
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
        if self.input_mode:
            # 输入模式：显示输入提示和缓冲区
            # 如果输入太长,只显示最后的部分
            display_buffer = self.input_buffer
            max_display_len = 80  # 最多显示80个字符
            if len(display_buffer) > max_display_len:
                display_buffer = "..." + display_buffer[-(max_display_len-3):]

            footer_text = Text(
                f"{self.status_message} {display_buffer}▊",
                style=THEME['warning'],
                justify="left",
                overflow="ignore"  # 不截断文本
            )
        elif self.status_message:
            # 显示状态消息
            footer_text = Text(
                f"进程: {len(self.claude_processes)} | {self.status_message} | 按 p 标记, u 取消标记 | Ctrl+C 退出",
                style=THEME['primary'],
                justify="center"
            )
            # 清空状态消息（3秒后）
            if not hasattr(self, '_status_message_time'):
                self._status_message_time = time.time()
            elif time.time() - self._status_message_time > 3:
                self.status_message = ""
                delattr(self, '_status_message_time')
        else:
            # 默认状态
            footer_text = Text(
                f"进程: {len(self.claude_processes)} | 按 p 标记会话, u 取消标记 | Ctrl+C 退出",
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
        table.add_column("", width=4, no_wrap=True)  # 状态图标 (increased from 2 to 4 to accommodate both pinned and active icons)
        table.add_column("项目", min_width=15, max_width=20, overflow="fold")  # 恢复原宽度并允许换行
        table.add_column("TodoWrite进度", min_width=40, max_width=60, overflow="ellipsis")
        table.add_column("会话ID", width=36, no_wrap=True)  # 显示完整UUID

        # 显示活跃会话和被标记的会话
        displayed_sessions = []
        for session in self.sessions.values():
            if session.is_active or session.is_pinned:
                displayed_sessions.append(session)

        sorted_sessions = sorted(
            displayed_sessions,
            key=lambda s: (s.is_pinned, s.last_activity),  # 标记的会话优先，然后按最后活动时间排序
            reverse=True
        )

        # 只显示前20个会话
        for session in sorted_sessions[:20]:
            # 状态图标：标记的会话显示📌，活跃的会话显示🟢
            if session.is_pinned and session.is_active:
                status_icon = "📌🟢"  # 既是标记又是活跃
            elif session.is_pinned:
                status_icon = "📌"   # 只是标记
            else:
                status_icon = "🟢"   # 只是活跃

            # TodoWrite进度
            if session.todos:
                todo_progress = session.todo_progress
            else:
                todo_progress = "无任务"

            # 使用绝对路径作为项目名，不进行特殊处理
            project_name = session.project_name

            table.add_row(
                status_icon,
                Text(project_name, style=THEME['text']),
                Text(todo_progress, overflow="ellipsis"),
                session.session_id  # 显示完整的session_id
            )

        # 如果没有会话，显示提示
        if not displayed_sessions:
            table.add_row(
                "🔴",
                Text("无活跃或标记的会话", style=THEME['text_secondary']),
                Text("无任务", style=THEME['text_secondary']),
                "-"
            )

        return table

    def create_todos_panel(self) -> Table:
        """创建TodoWrite汇总面板"""
        table = Table(show_header=False, box=None)
        table.add_column()

        # 只统计活跃会话的TodoWrite
        active_todos = []
        active_sessions = [s for s in self.sessions.values() if s.is_active]
        for session in active_sessions:
            for todo in session.todos:
                active_todos.append((session, todo))

        # 按时间排序，显示最新的
        active_todos.sort(key=lambda x: x[1].timestamp, reverse=True)

        # 状态统计
        stats = defaultdict(int)
        for _, todo in active_todos:
            stats[todo.status] += 1

        # 添加统计行
        stats_text = f"✅ 已完成: {stats['completed']}  🔄 进行中: {stats['in_progress']}  ⏳ 待处理: {stats['pending']}"
        table.add_row(Text(stats_text, style=THEME['text']))
        table.add_row("")  # 空行

        # 显示最近的任务
        table.add_row(Text("最新任务:", style=THEME['info']))
        for session, todo in active_todos[:10]:
            project = session.project_name.split('/')[-1]
            text = f"{todo.status_icon} [{project}] {todo.content}"
            style = THEME['success'] if todo.status == "completed" else THEME['warning'] if todo.status == "in_progress" else THEME['text_secondary']
            table.add_row(Text(text, style=style, overflow="ellipsis"))

        # 如果没有活跃会话的TodoWrite，显示提示
        if not active_todos:
            table.add_row(Text("无活跃会话的TodoWrite任务", style=THEME['text_secondary']))

        return table

    def toggle_pin_session(self, session_id: str):
        """切换会话的标记状态"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.is_pinned = not session.is_pinned
            if session.is_pinned:
                self.console.print(f"[{THEME['success']}]📌 会话已标记: {session.project_name}[/]")
            else:
                self.console.print(f"[{THEME['warning']}]⚪ 会话已取消标记: {session.project_name}[/]")

    async def run_ui(self):
        """运行UI循环"""
        with Live(
            self.create_dashboard(),
            refresh_per_second=4,  # 提高刷新率以更好地显示输入
            console=self.console
        ) as live:
            try:
                while self.running:
                    # 检查是否有键盘输入来处理标记操作
                    if self.console.is_terminal:
                        try:
                            # 检查键盘输入（非阻塞）
                            if self.console.size:
                                # 这里我们模拟键盘输入检测
                                # 实际上rich Live不直接支持键盘输入，我们需要使用其他方式
                                pass
                        except:
                            pass

                    # 更新UI
                    live.update(self.create_dashboard())

                    # 清理非活跃会话（2分钟内无活动）- 但保留标记的会话
                    current_time = datetime.now()
                    for session_id in list(self.active_sessions):
                        if session_id in self.sessions:
                            session = self.sessions[session_id]
                            # 对于标记的会话，不改变其活跃状态
                            if session.is_pinned:
                                continue
                            try:
                                file_stat = Path(session.file_path).stat()
                                file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
                                # 使用文件修改时间来判断是否活跃
                                if (current_time - file_mtime).total_seconds() > 120:  # 2分钟
                                    session.is_active = False
                                    self.active_sessions.discard(session_id)
                            except:
                                # 如果无法获取文件状态，使用时间戳判断
                                if (current_time - session.last_activity).total_seconds() > 120:  # 2分钟
                                    session.is_active = False
                                    self.active_sessions.discard(session_id)

                    # 定期检查所有会话的文件修改时间（每5秒）
                    if int(current_time.timestamp()) % 5 == 0:
                        for session in self.sessions.values():
                            try:
                                file_stat = Path(session.file_path).stat()
                                file_mtime = datetime.fromtimestamp(file_stat.st_mtime)

                                # 更新会话的最后活动时间为文件修改时间
                                session.last_activity = file_mtime

                                # 如果文件最近2分钟内有修改，但会话未标记为活跃
                                if (current_time - file_mtime).total_seconds() < 120:  # 2分钟
                                    if not session.is_active:
                                        session.is_active = True
                                        self.active_sessions.add(session.session_id)
                                # 如果文件超过2分钟没有修改，标记为非活跃
                                # 但要保留标记会话的显示状态
                                else:
                                    if session.is_active and not session.is_pinned:
                                        session.is_active = False
                                        self.active_sessions.discard(session.session_id)
                            except:
                                pass

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