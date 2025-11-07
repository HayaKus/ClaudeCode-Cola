"""
进程监控模块
"""
import psutil
import subprocess
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from .models import Session, ProcessInfo, PerformanceInfo, SessionStatus, TodoProgress


class ProcessMonitor:
    """进程监控器"""

    def __init__(self):
        """初始化监控器"""
        self.claude_process_pattern = re.compile(r'claude.*code')
        self.window_title_pattern = re.compile(r'\[CCCL\]\s+(.+)\s+-\s+(\w+)')

    def find_claude_processes(self) -> List[Dict]:
        """查找所有 Claude Code 进程"""
        processes = []

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    # 检查进程命令行是否包含 claude code
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'claude' in cmdline and ('code' in cmdline or '-r' in cmdline):
                        # 提取会话 ID
                        session_id = self._extract_session_id(cmdline)
                        if session_id:
                            processes.append({
                                'pid': proc.info['pid'],
                                'session_id': session_id,
                                'cmdline': cmdline,
                                'create_time': proc.info['create_time']
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"查找进程时出错: {e}")

        return processes

    def _extract_session_id(self, cmdline: str) -> Optional[str]:
        """从命令行提取会话 ID"""
        # 匹配 -r 参数后的会话 ID
        match = re.search(r'-r\s+(\w+)', cmdline)
        if match:
            return match.group(1)

        # 如果是新启动的会话，可能需要其他方式获取 ID
        # 这里可以通过其他方式实现
        return None

    def get_process_performance(self, pid: int) -> Optional[PerformanceInfo]:
        """获取进程性能信息"""
        try:
            process = psutil.Process(pid)

            # 获取 CPU 使用率（需要两次调用之间有间隔）
            cpu_percent = process.cpu_percent(interval=0.1)

            # 获取内存使用量（MB）
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            # 计算非活跃时间（这里简化处理，实际需要更复杂的逻辑）
            inactive_minutes = 0

            return PerformanceInfo(
                cpu_percent=cpu_percent,
                memory_mb=round(memory_mb, 2),
                inactive_minutes=inactive_minutes
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def get_iterm_windows(self) -> List[Dict]:
        """获取 iTerm2 窗口信息"""
        windows = []

        # 使用 AppleScript 获取 iTerm2 窗口信息
        script = """
        tell application "iTerm"
            set windowList to {}
            repeat with w in windows
                set windowInfo to {}
                set windowId to id of w
                set windowTitle to name of w
                set sessionCount to count of sessions of current tab of w

                repeat with s in sessions of current tab of w
                    set sessionName to name of s
                    set sessionInfo to {windowId:windowId, windowTitle:windowTitle, sessionName:sessionName}
                    copy sessionInfo to end of windowList
                end repeat
            end repeat
            return windowList
        end tell
        """

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )

            # 解析输出
            output = result.stdout.strip()
            if output:
                # 解析 AppleScript 返回的列表
                # 这里需要更复杂的解析逻辑
                # 暂时返回空列表
                pass

        except subprocess.CalledProcessError as e:
            print(f"获取 iTerm2 窗口信息失败: {e}")

        return windows

    def match_session_with_window(self, session_id: str) -> Optional[Tuple[str, str]]:
        """匹配会话与 iTerm2 窗口"""
        # 这是一个简化的实现
        # 实际需要通过 AppleScript 获取窗口标题并匹配

        script = f"""
        tell application "iTerm"
            repeat with w in windows
                set windowTitle to name of w
                if windowTitle contains "{session_id}" then
                    return {{id of w as string, windowTitle}}
                end if
            end repeat
            return ""
        end tell
        """

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )

            output = result.stdout.strip()
            if output and output != '""':
                # 解析返回的窗口 ID 和标题
                # 这里需要更复杂的解析
                parts = output.split(',')
                if len(parts) >= 2:
                    window_id = parts[0].strip()
                    window_title = parts[1].strip()
                    return (window_id, window_title)
        except subprocess.CalledProcessError:
            pass

        return None

    def extract_session_name_from_title(self, title: str) -> Optional[str]:
        """从窗口标题提取会话名称"""
        match = self.window_title_pattern.match(title)
        if match:
            return match.group(1).strip()
        return None

    def get_todo_progress(self, session_id: str, work_dir: str) -> Optional[TodoProgress]:
        """获取会话的 TodoWrite 进度"""
        # 这里需要实现读取 TodoWrite 数据的逻辑
        # 暂时返回模拟数据
        return None

    def check_session_status(self, pid: int) -> SessionStatus:
        """检查会话状态"""
        try:
            process = psutil.Process(pid)
            if process.is_running():
                # 检查进程状态
                status = process.status()
                if status == psutil.STATUS_ZOMBIE:
                    return SessionStatus.CRASHED
                elif status in [psutil.STATUS_STOPPED, psutil.STATUS_IDLE]:
                    return SessionStatus.PAUSED
                else:
                    return SessionStatus.RUNNING
            else:
                return SessionStatus.STOPPED
        except psutil.NoSuchProcess:
            return SessionStatus.STOPPED