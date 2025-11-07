"""测试会话管理器"""
import pytest
import tempfile
from pathlib import Path
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.session_manager import SessionManager
from src.core.models import SessionStatus


class TestSessionManager:
    """测试会话管理器"""

    def test_create_session(self):
        """测试创建会话"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(Path(tmpdir))

            # 创建会话
            session = manager.create_session(
                name="测试会话",
                work_dir="~/test",
                tags=["test", "demo"]
            )

            assert session.id is not None
            assert session.name == "测试会话"
            assert session.work_dir == os.path.expanduser("~/test")
            assert session.tags == ["test", "demo"]

            # 验证会话已添加到活跃列表
            active_sessions = manager.get_active_sessions()
            assert len(active_sessions) == 1
            assert active_sessions[0].id == session.id

    def test_close_session(self):
        """测试关闭会话"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(Path(tmpdir))

            # 创建会话
            session = manager.create_session("测试会话", "~/test")

            # 关闭会话
            success = manager.close_session(session.id)
            assert success == True

            # 验证会话已移到已关闭列表
            active_sessions = manager.get_active_sessions()
            assert len(active_sessions) == 0

            closed_sessions = manager.get_closed_sessions()
            assert len(closed_sessions) == 1
            assert closed_sessions[0].id == session.id
            assert closed_sessions[0].status == SessionStatus.STOPPED

    def test_star_session(self):
        """测试标记重要会话"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(Path(tmpdir))

            # 创建会话
            session = manager.create_session("测试会话", "~/test")
            assert session.is_starred == False

            # 标记为重要
            success = manager.star_session(session.id)
            assert success == True

            # 验证标记状态
            active_sessions = manager.get_active_sessions()
            assert active_sessions[0].is_starred == True

            # 再次切换
            manager.star_session(session.id)
            active_sessions = manager.get_active_sessions()
            assert active_sessions[0].is_starred == False

    def test_save_load_sessions(self):
        """测试保存和加载会话数据"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建并保存会话
            manager1 = SessionManager(Path(tmpdir))
            session = manager1.create_session("持久化测试", "~/persist")
            session_id = session.id

            # 创建新的管理器实例，加载数据
            manager2 = SessionManager(Path(tmpdir))
            active_sessions = manager2.get_active_sessions()

            assert len(active_sessions) == 1
            assert active_sessions[0].id == session_id
            assert active_sessions[0].name == "持久化测试"

    def test_get_templates(self):
        """测试获取模板"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(Path(tmpdir))
            templates = manager.get_templates()

            # 应该有默认模板
            assert len(templates) >= 3

            # 验证默认模板存在
            template_ids = [t.id for t in templates]
            assert "tpl_frontend" in template_ids
            assert "tpl_api" in template_ids
            assert "tpl_bug_fix" in template_ids


import os  # 添加缺失的导入

if __name__ == "__main__":
    pytest.main([__file__, "-v"])