#!/usr/bin/env python3
"""
Claude Code Manager CLI 入口
"""
import click
import subprocess
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.main import main as run_manager
from src.core.config import ConfigManager
from src.core.session_manager import SessionManager


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Claude Code Manager - 你的智能会话管家"""
    if ctx.invoked_subcommand is None:
        # 默认运行主界面
        run_manager()


@cli.command()
def start():
    """启动 Claude Code Manager"""
    run_manager()


@cli.command()
def config():
    """编辑配置文件"""
    config_manager = ConfigManager()
    config_path = config_manager.config_path

    # 使用默认编辑器打开配置文件
    editor = subprocess.os.environ.get('EDITOR', 'nano')
    subprocess.call([editor, str(config_path)])


@cli.command()
@click.argument('session_name')
@click.option('--dir', '-d', 'work_dir', default='~', help='工作目录')
@click.option('--tags', '-t', multiple=True, help='标签')
def new(session_name, work_dir, tags):
    """快速创建新会话"""
    from src.core.iterm2_integration import ITerm2Integration

    # 检查 iTerm2
    iterm2 = ITerm2Integration()
    if not iterm2.is_iterm2_running():
        click.echo("错误：iTerm2 未运行，请先启动 iTerm2")
        sys.exit(1)

    # 创建会话
    session_manager = SessionManager()
    session = session_manager.create_session(session_name, work_dir, list(tags))

    # 在 iTerm2 中启动
    success = iterm2.create_new_window(session.name, session.id, session.work_dir)

    if success:
        click.echo(f"✅ 会话 '{session.name}' 创建成功！")
    else:
        click.echo(f"❌ 创建会话失败")


@cli.command()
def list():
    """列出所有会话"""
    session_manager = SessionManager()
    session_manager.refresh_sessions()

    # 活跃会话
    active_sessions = session_manager.get_active_sessions()
    if active_sessions:
        click.echo("\n🟢 活跃会话:")
        for session in active_sessions:
            star = "⭐ " if session.is_starred else ""
            click.echo(f"  {star}{session.name} ({session.id[:6]}) - {session.work_dir}")

    # 关闭的会话
    closed_sessions = session_manager.get_closed_sessions(hours=24)
    if closed_sessions:
        click.echo("\n🔴 最近关闭:")
        for session in closed_sessions[:5]:
            click.echo(f"  {session.name} ({session.id[:6]}) - {session.duration or 'N/A'}")


@cli.command()
def doctor():
    """检查系统环境"""
    from src.core.iterm2_integration import ITerm2Integration

    click.echo("正在检查系统环境...\n")

    # 检查 iTerm2
    iterm2 = ITerm2Integration()
    if iterm2.is_iterm2_running():
        click.echo("✅ iTerm2 正在运行")
    else:
        click.echo("❌ iTerm2 未运行")

    # 检查 Claude
    try:
        result = subprocess.run(
            ["which", "claude"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            click.echo(f"✅ Claude CLI 已安装: {result.stdout.strip()}")
        else:
            click.echo("❌ Claude CLI 未安装")
    except:
        click.echo("❌ 无法检查 Claude CLI")

    # 检查配置
    config_manager = ConfigManager()
    if config_manager.config.claude_api.api_key:
        click.echo("✅ Claude API 已配置")
    else:
        click.echo("⚠️  Claude API 未配置（AI 助手功能将不可用）")

    # 检查数据目录
    data_dir = Path.home() / "Code" / "ClaudeCode-Cola" / ".claude-code-manager"
    if data_dir.exists():
        click.echo(f"✅ 数据目录存在: {data_dir}")
    else:
        click.echo(f"⚠️  数据目录不存在: {data_dir}")


@cli.command()
def version():
    """显示版本信息"""
    click.echo("Claude Code Manager (ClaudeCode-Cola) v1.0.0")
    click.echo("像可口可乐一样让你的编程体验充满活力！")


if __name__ == '__main__':
    cli()