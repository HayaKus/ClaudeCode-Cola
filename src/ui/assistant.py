"""
AI 助手模块
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from anthropic import Anthropic

from ..core.models import Session, SessionStatus
from ..core.session_manager import SessionManager
from ..core.iterm2_integration import ITerm2Integration
from ..core.config import ConfigManager


class Assistant:
    """AI 助手类"""

    def __init__(self, session_manager: SessionManager):
        """初始化助手"""
        self.session_manager = session_manager
        self.iterm2 = ITerm2Integration()
        self.config_manager = ConfigManager()

        # 初始化 Claude API 客户端
        api_config = self.config_manager.config.claude_api
        if api_config.api_key:
            self.client = Anthropic(
                api_key=api_config.api_key,
                base_url=api_config.base_url
            )
            self.model = api_config.model_name
        else:
            self.client = None
            self.model = None

        # 上下文历史
        self.context_history: List[Dict[str, str]] = []

    def is_available(self) -> bool:
        """检查助手是否可用"""
        return self.client is not None

    async def process_message(self, user_message: str) -> str:
        """处理用户消息"""
        if not self.is_available():
            return "AI 助手未配置。请先配置 Claude API Key。"

        # 构建系统提示
        system_prompt = self._build_system_prompt()

        # 构建消息历史
        messages = self._build_messages(user_message)

        try:
            # 调用 Claude API
            response = self.client.messages.create(
                model=self.model,
                messages=messages,
                system=system_prompt,
                max_tokens=1000
            )

            # 提取响应
            assistant_message = response.content[0].text

            # 保存到历史
            self.context_history.append({"role": "user", "content": user_message})
            self.context_history.append({"role": "assistant", "content": assistant_message})

            # 保持历史记录在合理长度
            if len(self.context_history) > 20:
                self.context_history = self.context_history[-20:]

            # 执行助手建议的操作
            await self._execute_actions(assistant_message)

            return assistant_message

        except Exception as e:
            return f"处理消息时出错：{e}"

    def _build_system_prompt(self) -> str:
        """构建系统提示"""
        active_sessions = self.session_manager.get_active_sessions()
        closed_sessions = self.session_manager.get_closed_sessions()

        # 会话状态摘要
        session_summary = f"""
当前会话状态：
- 活跃会话数：{len(active_sessions)}
- 最近关闭的会话数：{len(closed_sessions)}

活跃会话详情：
"""
        for session in active_sessions:
            session_summary += f"""
- {session.name} (ID: {session.id[:6]})
  目录：{session.work_dir}
  运行时长：{self._format_duration(datetime.now() - session.created_at)}
  """
            if session.todo_progress:
                session_summary += f"进度：{session.todo_progress.completed}/{session.todo_progress.total} ({session.todo_progress.percentage:.0f}%)\n"
            if session.performance:
                session_summary += f"  性能：CPU {session.performance.cpu_percent:.1f}%, 内存 {session.performance.memory_mb:.0f}MB\n"
                if session.performance.inactive_minutes > 30:
                    session_summary += f"  ⚠️ 已闲置 {session.performance.inactive_minutes} 分钟\n"

        system_prompt = f"""
你是 Claude Code Manager 的智能助手。你的职责是帮助用户管理 Claude Code 会话。

{session_summary}

你可以执行以下操作：
1. 分析会话状态，提供优化建议
2. 创建新会话：使用 [CREATE_SESSION: name, work_dir, tags] 格式
3. 关闭会话：使用 [CLOSE_SESSION: session_id] 格式
4. 恢复会话：使用 [RESTORE_SESSION: session_id] 格式
5. 标记重要会话：使用 [STAR_SESSION: session_id] 格式
6. 发送通知：使用 [NOTIFY: title, message] 格式

请用友好、专业的语气回复，并在需要执行操作时使用上述格式。
"""
        return system_prompt

    def _build_messages(self, user_message: str) -> List[Dict[str, str]]:
        """构建消息列表"""
        messages = []

        # 添加历史消息
        for msg in self.context_history[-10:]:  # 只保留最近10条
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # 添加当前消息
        messages.append({
            "role": "user",
            "content": user_message
        })

        return messages

    def _format_duration(self, duration: timedelta) -> str:
        """格式化时长"""
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)

        if hours > 0:
            return f"{hours}小时 {minutes}分钟"
        else:
            return f"{minutes}分钟"

    async def _execute_actions(self, message: str) -> None:
        """执行助手建议的操作"""
        # 解析并执行创建会话命令
        if "[CREATE_SESSION:" in message:
            start = message.find("[CREATE_SESSION:") + 16
            end = message.find("]", start)
            if end > start:
                params = message[start:end].split(",")
                if len(params) >= 2:
                    name = params[0].strip()
                    work_dir = params[1].strip()
                    tags = [t.strip() for t in params[2:]] if len(params) > 2 else []

                    # 创建会话
                    session = self.session_manager.create_session(name, work_dir, tags)
                    # 启动会话
                    self.iterm2.create_new_window(session.name, session.id, session.work_dir)

        # 解析并执行关闭会话命令
        if "[CLOSE_SESSION:" in message:
            start = message.find("[CLOSE_SESSION:") + 15
            end = message.find("]", start)
            if end > start:
                session_id = message[start:end].strip()
                self.session_manager.close_session(session_id)

        # 解析并执行恢复会话命令
        if "[RESTORE_SESSION:" in message:
            start = message.find("[RESTORE_SESSION:") + 17
            end = message.find("]", start)
            if end > start:
                session_id = message[start:end].strip()
                # 查找会话
                session = next((s for s in self.session_manager.get_closed_sessions() if s.id == session_id), None)
                if session:
                    self.iterm2.restore_session(session.id, session.name, session.work_dir)

        # 解析并执行标记会话命令
        if "[STAR_SESSION:" in message:
            start = message.find("[STAR_SESSION:") + 14
            end = message.find("]", start)
            if end > start:
                session_id = message[start:end].strip()
                self.session_manager.star_session(session_id)

        # 解析并执行通知命令
        if "[NOTIFY:" in message:
            start = message.find("[NOTIFY:") + 8
            end = message.find("]", start)
            if end > start:
                params = message[start:end].split(",", 1)
                if len(params) == 2:
                    title = params[0].strip()
                    notify_message = params[1].strip()
                    self.iterm2.send_notification(title, notify_message, "Claude Code Manager")

    def analyze_work_status(self) -> str:
        """分析工作状态"""
        active_sessions = self.session_manager.get_active_sessions()

        if not active_sessions:
            return "当前没有活跃的会话。你可以创建一个新会话开始工作。"

        analysis = "**当前工作状态分析：**\n\n"

        # 统计信息
        total_sessions = len(active_sessions)
        completed_sessions = sum(1 for s in active_sessions if s.todo_progress and s.todo_progress.percentage == 100)
        high_cpu_sessions = sum(1 for s in active_sessions if s.performance and s.performance.cpu_percent > 80)
        inactive_sessions = sum(1 for s in active_sessions if s.performance and s.performance.inactive_minutes > 30)

        analysis += f"- 活跃会话数：{total_sessions}\n"
        if completed_sessions > 0:
            analysis += f"- 已完成的会话：{completed_sessions} 个（建议关闭以释放资源）\n"
        if high_cpu_sessions > 0:
            analysis += f"- 高CPU使用：{high_cpu_sessions} 个会话\n"
        if inactive_sessions > 0:
            analysis += f"- 长时间未活动：{inactive_sessions} 个会话\n"

        # 详细分析每个会话
        analysis += "\n**会话详情：**\n"
        for session in active_sessions:
            analysis += f"\n📌 **{session.name}**\n"

            # 进度分析
            if session.todo_progress:
                percentage = session.todo_progress.percentage
                if percentage == 100:
                    analysis += "   ✅ 所有任务已完成，建议关闭会话\n"
                elif percentage >= 75:
                    analysis += f"   📈 进度良好 ({percentage:.0f}%)，即将完成\n"
                elif percentage >= 50:
                    analysis += f"   ⏳ 进度过半 ({percentage:.0f}%)，继续加油\n"
                else:
                    analysis += f"   🚀 刚开始 ({percentage:.0f}%)，保持专注\n"

            # 性能分析
            if session.performance:
                if session.performance.cpu_percent > 80:
                    analysis += "   🔥 CPU使用率较高，检查是否有死循环\n"
                if session.performance.inactive_minutes > 60:
                    analysis += f"   💤 已闲置 {session.performance.inactive_minutes} 分钟，考虑暂停或关闭\n"
                elif session.performance.inactive_minutes > 30:
                    analysis += f"   ⏸️ 已闲置 {session.performance.inactive_minutes} 分钟\n"

            # 运行时长
            duration = datetime.now() - session.created_at
            if duration.total_seconds() > 3 * 3600:  # 超过3小时
                analysis += f"   ⏰ 已运行 {self._format_duration(duration)}，建议休息一下\n"

        return analysis

    def suggest_next_action(self) -> str:
        """建议下一步操作"""
        active_sessions = self.session_manager.get_active_sessions()
        suggestions = []

        # 检查已完成的会话
        completed = [s for s in active_sessions if s.todo_progress and s.todo_progress.percentage == 100]
        if completed:
            sessions_str = ", ".join([s.name for s in completed])
            suggestions.append(f"关闭已完成的会话：{sessions_str}")

        # 检查长时间未活动的会话
        inactive = [s for s in active_sessions if s.performance and s.performance.inactive_minutes > 60]
        if inactive:
            sessions_str = ", ".join([s.name for s in inactive])
            suggestions.append(f"检查或关闭长时间未活动的会话：{sessions_str}")

        # 检查高资源占用
        high_cpu = [s for s in active_sessions if s.performance and s.performance.cpu_percent > 80]
        if high_cpu:
            sessions_str = ", ".join([s.name for s in high_cpu])
            suggestions.append(f"检查高CPU占用的会话：{sessions_str}")

        if suggestions:
            return "**建议的下一步操作：**\n" + "\n".join(f"- {s}" for s in suggestions)
        else:
            return "当前状态良好，继续保持！"