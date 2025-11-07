"""
会话管理器
"""
import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from .models import Session, SessionStatus, Template, ProcessInfo
from .monitor import ProcessMonitor
from .config import ConfigManager


class SessionManager:
    """会话管理器"""

    def __init__(self, data_dir: Optional[Path] = None):
        """初始化会话管理器"""
        if data_dir is None:
            self.data_dir = Path.home() / "Code" / "ClaudeCode-Cola" / ".claude-code-manager"
        else:
            self.data_dir = data_dir

        self.sessions_file = self.data_dir / "sessions.json"
        self.monitor = ProcessMonitor()
        self.config_manager = ConfigManager()

        # 确保数据目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 加载现有数据
        self.active_sessions: Dict[str, Session] = {}
        self.closed_sessions: List[Session] = []
        self.templates: List[Template] = []
        self.load_data()

        # 初始化默认模板
        self._init_default_templates()

    def load_data(self) -> None:
        """加载会话数据"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 加载活跃会话
                for session_id, session_data in data.get("active_sessions", {}).items():
                    self.active_sessions[session_id] = Session.from_dict(session_data)

                # 加载已关闭会话
                for session_data in data.get("closed_sessions", []):
                    self.closed_sessions.append(Session.from_dict(session_data))

                # 加载模板
                for template_data in data.get("templates", []):
                    self.templates.append(Template.from_dict(template_data))

            except Exception as e:
                print(f"加载会话数据失败: {e}")

    def save_data(self) -> None:
        """保存会话数据"""
        data = {
            "active_sessions": {
                session_id: session.to_dict()
                for session_id, session in self.active_sessions.items()
            },
            "closed_sessions": [
                session.to_dict() for session in self.closed_sessions[-20:]  # 只保留最近20个
            ],
            "templates": [
                template.to_dict() for template in self.templates
            ]
        }

        with open(self.sessions_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _init_default_templates(self) -> None:
        """初始化默认模板"""
        default_templates = [
            {
                "id": "tpl_frontend",
                "name": "前端开发",
                "work_dir": "~/projects/frontend",
                "name_pattern": "前端-{feature}-{date}",
                "tags": ["前端", "React"],
                "default_todos": [
                    "创建组件结构",
                    "实现业务逻辑",
                    "添加样式",
                    "编写单元测试",
                    "更新文档"
                ]
            },
            {
                "id": "tpl_api",
                "name": "API开发",
                "work_dir": "~/projects/backend",
                "name_pattern": "API-{feature}-{date}",
                "tags": ["API", "后端"],
                "default_todos": [
                    "设计 API 接口",
                    "实现数据模型",
                    "编写业务逻辑",
                    "添加单元测试",
                    "编写 API 文档"
                ]
            },
            {
                "id": "tpl_bug_fix",
                "name": "Bug修复",
                "work_dir": "~/projects",
                "name_pattern": "修复-{issue}-{date}",
                "tags": ["Bug修复"],
                "default_todos": [
                    "复现问题",
                    "定位原因",
                    "修复代码",
                    "验证修复",
                    "添加测试用例"
                ]
            }
        ]

        # 添加不存在的默认模板
        existing_ids = {t.id for t in self.templates}
        for template_data in default_templates:
            if template_data["id"] not in existing_ids:
                self.templates.append(Template.from_dict(template_data))

    def refresh_sessions(self) -> None:
        """刷新会话状态"""
        # 获取当前运行的 Claude 进程
        processes = self.monitor.find_claude_processes()

        # 更新现有会话状态
        for session_id, session in self.active_sessions.items():
            # 查找对应的进程
            process = next((p for p in processes if p['session_id'] == session_id), None)

            if process:
                # 更新进程信息
                pid = process['pid']
                session.process_info = ProcessInfo(
                    pid=pid,
                    iTerm_window_id="",
                    iTerm_window_title=""
                )

                # 获取窗口信息
                window_info = self.monitor.match_session_with_window(session_id)
                if window_info:
                    session.process_info.iTerm_window_id = window_info[0]
                    session.process_info.iTerm_window_title = window_info[1]

                    # 从窗口标题提取会话名称（如果还没有名称）
                    if session.name.startswith("未命名"):
                        name = self.monitor.extract_session_name_from_title(window_info[1])
                        if name:
                            session.name = name

                # 更新性能信息
                performance = self.monitor.get_process_performance(pid)
                if performance:
                    session.performance = performance

                # 更新状态
                session.status = self.monitor.check_session_status(pid)
                session.last_active = datetime.now()

            else:
                # 进程不存在了，标记为已停止
                if session.status != SessionStatus.STOPPED:
                    session.status = SessionStatus.STOPPED
                    session.closed_at = datetime.now()
                    session.closed_reason = "normal"

                    # 计算运行时长
                    duration = session.closed_at - session.created_at
                    hours = int(duration.total_seconds() // 3600)
                    minutes = int((duration.total_seconds() % 3600) // 60)
                    session.duration = f"{hours}h {minutes}m"

                    # 移到已关闭会话
                    self.closed_sessions.append(session)
                    del self.active_sessions[session_id]

        # 发现新的会话
        existing_ids = set(self.active_sessions.keys())
        for process in processes:
            session_id = process['session_id']
            if session_id not in existing_ids:
                # 创建新的会话记录
                session = Session(
                    id=session_id,
                    name=f"未命名-{session_id[:6]}",
                    work_dir="~",  # 需要从其他地方获取
                    created_at=datetime.fromtimestamp(process['create_time']),
                    last_active=datetime.now(),
                    process_info=ProcessInfo(
                        pid=process['pid'],
                        iTerm_window_id="",
                        iTerm_window_title=""
                    )
                )

                # 尝试获取窗口信息
                window_info = self.monitor.match_session_with_window(session_id)
                if window_info:
                    session.process_info.iTerm_window_id = window_info[0]
                    session.process_info.iTerm_window_title = window_info[1]

                    # 从窗口标题提取会话名称
                    name = self.monitor.extract_session_name_from_title(window_info[1])
                    if name:
                        session.name = name

                self.active_sessions[session_id] = session

        # 保存数据
        self.save_data()

    def create_session(self, name: str, work_dir: str, tags: List[str] = None,
                      template_id: Optional[str] = None) -> Session:
        """创建新会话"""
        session_id = str(uuid.uuid4())[:8]

        # 如果使用模板
        if template_id:
            template = next((t for t in self.templates if t.id == template_id), None)
            if template:
                # 应用模板
                work_dir = work_dir or template.work_dir
                tags = tags or template.tags
                # 处理名称模式
                name = template.name_pattern.format(
                    feature=name,
                    date=datetime.now().strftime("%Y%m%d"),
                    time=datetime.now().strftime("%H%M")
                )

        session = Session(
            id=session_id,
            name=name,
            work_dir=os.path.expanduser(work_dir),
            created_at=datetime.now(),
            last_active=datetime.now(),
            tags=tags or []
        )

        self.active_sessions[session_id] = session
        self.save_data()

        return session

    def close_session(self, session_id: str, reason: str = "normal") -> bool:
        """关闭会话"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.status = SessionStatus.STOPPED
            session.closed_at = datetime.now()
            session.closed_reason = reason

            # 计算运行时长
            duration = session.closed_at - session.created_at
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            session.duration = f"{hours}h {minutes}m"

            # 移到已关闭会话
            self.closed_sessions.append(session)
            del self.active_sessions[session_id]

            self.save_data()
            return True
        return False

    def star_session(self, session_id: str) -> bool:
        """标记/取消标记重要会话"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.is_starred = not session.is_starred
            self.save_data()
            return True
        return False

    def add_note(self, session_id: str, note: str) -> bool:
        """添加会话备注"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.notes = note
            self.save_data()
            return True
        return False

    def update_session_name(self, session_id: str, name: str) -> bool:
        """更新会话名称"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.name = name
            self.save_data()
            return True
        return False

    def get_active_sessions(self) -> List[Session]:
        """获取所有活跃会话"""
        # 按是否星标和创建时间排序
        sessions = list(self.active_sessions.values())
        sessions.sort(key=lambda s: (not s.is_starred, s.created_at), reverse=True)
        return sessions

    def get_closed_sessions(self, hours: int = 24) -> List[Session]:
        """获取最近关闭的会话"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_sessions = [
            s for s in self.closed_sessions
            if s.closed_at and s.closed_at > cutoff_time
        ]
        # 按关闭时间排序
        recent_sessions.sort(key=lambda s: s.closed_at, reverse=True)
        return recent_sessions[:20]  # 最多返回20个

    def save_as_template(self, session_id: str, template_name: str) -> bool:
        """将会话保存为模板"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            template = Template(
                id=f"tpl_custom_{str(uuid.uuid4())[:8]}",
                name=template_name,
                work_dir=session.work_dir,
                name_pattern=f"{session.name}-{{date}}",
                tags=session.tags,
                default_todos=[]  # 需要从 TodoWrite 获取
            )
            self.templates.append(template)
            self.save_data()
            return True
        return False

    def get_templates(self) -> List[Template]:
        """获取所有模板"""
        return self.templates