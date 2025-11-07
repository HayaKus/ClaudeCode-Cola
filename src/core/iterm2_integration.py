"""
iTerm2 集成模块
"""
import subprocess
import os
from typing import Optional, Tuple, List, Dict


class ITerm2Integration:
    """iTerm2 集成类"""

    @staticmethod
    def create_new_window(session_name: str, session_id: str, work_dir: str) -> bool:
        """创建新的 iTerm2 窗口并启动 Claude Code"""
        # 展开用户目录
        work_dir = os.path.expanduser(work_dir)

        # 构建窗口标题
        window_title = f"[CCCL] {session_name} - {session_id}"

        script = f'''
        tell application "iTerm"
            -- 创建新窗口
            create window with default profile

            -- 获取当前窗口和会话
            set currentWindow to current window
            set currentSession to current session of currentWindow

            -- 设置窗口标题
            tell currentWindow
                set name to "{window_title}"
            end tell

            -- 设置会话名称
            tell currentSession
                set name to "{window_title}"

                -- 切换到工作目录
                write text "cd {work_dir}"

                -- 启动 Claude Code
                write text "claude code --dangerously-skip-permissions"
            end tell

            return id of currentWindow
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"创建 iTerm2 窗口失败: {e}")
            print(f"错误输出: {e.stderr}")
            return False

    @staticmethod
    def restore_session(session_id: str, session_name: str, work_dir: Optional[str] = None) -> bool:
        """恢复会话"""
        # 构建窗口标题
        window_title = f"[CCCL] {session_name} - {session_id}"

        script_parts = ['''
        tell application "iTerm"
            -- 创建新窗口
            create window with default profile

            -- 获取当前窗口和会话
            set currentWindow to current window
            set currentSession to current session of currentWindow

            -- 设置窗口标题
            tell currentWindow
                set name to "{window_title}"
            end tell

            -- 设置会话名称
            tell currentSession
                set name to "{window_title}"
        ''']

        # 如果提供了工作目录，先切换
        if work_dir:
            work_dir = os.path.expanduser(work_dir)
            script_parts.append(f'''
                -- 切换到工作目录
                write text "cd {work_dir}"
            ''')

        script_parts.append(f'''
                -- 恢复 Claude Code 会话
                write text "claude -r {session_id}"
            end tell

            return id of currentWindow
        end tell
        ''')

        script = ''.join(script_parts).format(
            window_title=window_title,
            session_id=session_id,
            work_dir=work_dir
        )

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"恢复会话失败: {e}")
            print(f"错误输出: {e.stderr}")
            return False

    @staticmethod
    def attach_to_session(session_id: str, session_name: str) -> bool:
        """附加到现有会话（在新窗口中查看）"""
        window_title = f"[CCCL] {session_name} - {session_id} (附加)"

        script = f'''
        tell application "iTerm"
            -- 创建新窗口
            create window with default profile

            -- 获取当前窗口和会话
            set currentWindow to current window
            set currentSession to current session of currentWindow

            -- 设置窗口标题
            tell currentWindow
                set name to "{window_title}"
            end tell

            -- 设置会话名称
            tell currentSession
                set name to "{window_title}"

                -- 附加到会话
                write text "claude -a {session_id}"
            end tell

            return id of currentWindow
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"附加到会话失败: {e}")
            return False

    @staticmethod
    def get_window_info(window_id: str) -> Optional[Dict]:
        """获取窗口信息"""
        script = f'''
        tell application "iTerm"
            repeat with w in windows
                if (id of w as string) is "{window_id}" then
                    set windowTitle to name of w
                    set sessionCount to count of sessions of current tab of w

                    if sessionCount > 0 then
                        set firstSession to first session of current tab of w
                        set sessionName to name of firstSession
                        return {{windowId:id of w as string, windowTitle:windowTitle, sessionName:sessionName}}
                    end if
                end if
            end repeat
            return ""
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )

            output = result.stdout.strip()
            if output and output != '""':
                # 解析返回的信息
                # 这里需要更复杂的解析逻辑
                return None
        except subprocess.CalledProcessError:
            pass

        return None

    @staticmethod
    def find_windows_by_session_id(session_id: str) -> List[Tuple[str, str]]:
        """根据会话 ID 查找窗口"""
        script = f'''
        tell application "iTerm"
            set matchingWindows to {{}}

            repeat with w in windows
                set windowTitle to name of w
                if windowTitle contains "{session_id}" then
                    copy {{id of w as string, windowTitle}} to end of matchingWindows
                end if
            end repeat

            return matchingWindows
        end tell
        '''

        windows = []
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )

            output = result.stdout.strip()
            if output and output != '{}':
                # 解析返回的窗口列表
                # 这里需要实现 AppleScript 列表的解析
                # 暂时返回空列表
                pass
        except subprocess.CalledProcessError:
            pass

        return windows

    @staticmethod
    def close_window(window_id: str) -> bool:
        """关闭指定窗口"""
        script = f'''
        tell application "iTerm"
            repeat with w in windows
                if (id of w as string) is "{window_id}" then
                    close w
                    return true
                end if
            end repeat
            return false
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() == "true"
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def send_notification(title: str, message: str, subtitle: str = "") -> bool:
        """发送系统通知"""
        script = f'''
        tell application "iTerm"
            display notification "{message}" with title "{title}" subtitle "{subtitle}" sound name "Glass"
        end tell
        '''

        try:
            subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            # 如果 iTerm2 通知失败，尝试使用系统通知
            try:
                system_script = f'''
                display notification "{message}" with title "{title}" subtitle "{subtitle}" sound name "Glass"
                '''
                subprocess.run(
                    ['osascript', '-e', system_script],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return True
            except:
                return False

    @staticmethod
    def is_iterm2_running() -> bool:
        """检查 iTerm2 是否正在运行"""
        script = '''
        tell application "System Events"
            return (name of processes) contains "iTerm2"
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() == "true"
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def activate_window(window_id: str) -> bool:
        """激活指定窗口"""
        script = f'''
        tell application "iTerm"
            repeat with w in windows
                if (id of w as string) is "{window_id}" then
                    select w
                    activate
                    return true
                end if
            end repeat
            return false
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() == "true"
        except subprocess.CalledProcessError:
            return False