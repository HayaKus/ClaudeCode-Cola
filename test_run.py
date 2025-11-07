#!/usr/bin/env python3
"""测试运行脚本 - 用于快速测试基本功能"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parent))

def test_basic_imports():
    """测试基本导入"""
    print("测试基本导入...")
    try:
        from src.core.models import Session, SessionStatus
        from src.core.config import ConfigManager
        from src.core.session_manager import SessionManager
        from src.core.monitor import ProcessMonitor
        from src.core.iterm2_integration import ITerm2Integration
        from src.ui.interface import UserInterface
        from src.ui.assistant import Assistant
        print("✅ 所有导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_config_manager():
    """测试配置管理器"""
    print("\n测试配置管理器...")
    try:
        from src.core.config import ConfigManager
        config_manager = ConfigManager()
        print(f"✅ 配置文件路径: {config_manager.config_path}")
        print(f"   默认工作目录: {config_manager.config.general.default_work_dir}")
        return True
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        return False


def test_session_manager():
    """测试会话管理器"""
    print("\n测试会话管理器...")
    try:
        from src.core.session_manager import SessionManager
        session_manager = SessionManager()

        # 测试创建会话
        session = session_manager.create_session("测试会话", "~/test", ["test"])
        print(f"✅ 创建会话成功: {session.name} (ID: {session.id[:6]})")

        # 测试获取会话
        active_sessions = session_manager.get_active_sessions()
        print(f"   活跃会话数: {len(active_sessions)}")

        # 测试关闭会话
        success = session_manager.close_session(session.id)
        print(f"   关闭会话: {'成功' if success else '失败'}")

        return True
    except Exception as e:
        print(f"❌ 会话管理器测试失败: {e}")
        return False


def test_iterm2_integration():
    """测试 iTerm2 集成"""
    print("\n测试 iTerm2 集成...")
    try:
        from src.core.iterm2_integration import ITerm2Integration
        iterm2 = ITerm2Integration()

        is_running = iterm2.is_iterm2_running()
        print(f"✅ iTerm2 状态: {'运行中' if is_running else '未运行'}")

        if not is_running:
            print("   ⚠️  请启动 iTerm2 以使用完整功能")

        return True
    except Exception as e:
        print(f"❌ iTerm2 集成测试失败: {e}")
        return False


def test_process_monitor():
    """测试进程监控"""
    print("\n测试进程监控...")
    try:
        from src.core.monitor import ProcessMonitor
        monitor = ProcessMonitor()

        # 查找 Claude 进程
        processes = monitor.find_claude_processes()
        print(f"✅ 找到 {len(processes)} 个 Claude 进程")

        return True
    except Exception as e:
        print(f"❌ 进程监控测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("="*50)
    print("Claude Code Manager 功能测试")
    print("="*50)

    tests = [
        test_basic_imports,
        test_config_manager,
        test_session_manager,
        test_iterm2_integration,
        test_process_monitor
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    print(f"测试结果: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
        print("\n下一步:")
        print("1. 运行 ./install.sh 安装程序")
        print("2. 配置 API Key (编辑 ~/Code/ClaudeCode-Cola/.claude-code-manager/config.json)")
        print("3. 运行 cccl 启动管理器")
    else:
        print("\n❌ 部分测试失败，请检查错误信息")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)