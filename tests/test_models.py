"""测试数据模型"""
import pytest
from datetime import datetime
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.models import Session, SessionStatus, TodoProgress, PerformanceInfo, Template


class TestSession:
    """测试 Session 模型"""

    def test_session_creation(self):
        """测试创建会话"""
        session = Session(
            id="test123",
            name="测试会话",
            work_dir="~/test",
            tags=["test", "demo"]
        )

        assert session.id == "test123"
        assert session.name == "测试会话"
        assert session.work_dir == "~/test"
        assert session.tags == ["test", "demo"]
        assert session.status == SessionStatus.RUNNING
        assert session.is_starred == False

    def test_session_to_dict(self):
        """测试会话序列化"""
        session = Session(
            id="test123",
            name="测试会话",
            work_dir="~/test"
        )

        data = session.to_dict()
        assert data["id"] == "test123"
        assert data["name"] == "测试会话"
        assert data["work_dir"] == "~/test"
        assert "created_at" in data

    def test_session_from_dict(self):
        """测试会话反序列化"""
        data = {
            "id": "test123",
            "name": "测试会话",
            "work_dir": "~/test",
            "created_at": "2024-01-01T12:00:00",
            "status": "running"
        }

        session = Session.from_dict(data)
        assert session.id == "test123"
        assert session.name == "测试会话"
        assert session.status == SessionStatus.RUNNING


class TestTodoProgress:
    """测试 TodoProgress 模型"""

    def test_todo_progress_percentage(self):
        """测试进度计算"""
        progress = TodoProgress(total=10, completed=3)
        assert progress.percentage == 30.0

        progress = TodoProgress(total=0, completed=0)
        assert progress.percentage == 0.0

        progress = TodoProgress(total=5, completed=5)
        assert progress.percentage == 100.0


class TestTemplate:
    """测试 Template 模型"""

    def test_template_creation(self):
        """测试创建模板"""
        template = Template(
            id="tpl_test",
            name="测试模板",
            work_dir="~/projects",
            name_pattern="test-{feature}-{date}",
            tags=["test"],
            default_todos=["任务1", "任务2"]
        )

        assert template.id == "tpl_test"
        assert template.name == "测试模板"
        assert len(template.default_todos) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])