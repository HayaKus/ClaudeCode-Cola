#!/usr/bin/env python3
"""
Claude Monitor 测试版本 - 快速验证功能
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print

console = Console()

def parse_session_file(file_path):
    """解析单个会话文件"""
    todos = []
    message_count = 0
    last_message = ""

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())

                    # 统计消息
                    if data.get('type') in ['user', 'assistant']:
                        message_count += 1

                        # 提取用户消息
                        if data.get('type') == 'user':
                            message = data.get('message', {})
                            if isinstance(message.get('content'), str):
                                last_message = message['content'][:100]

                        # 查找TodoWrite
                        if data.get('type') == 'assistant':
                            message = data.get('message', {})
                            content = message.get('content', [])

                            for item in content:
                                if isinstance(item, dict) and item.get('type') == 'tool_use' and item.get('name') == 'TodoWrite':
                                    todos_data = item.get('input', {}).get('todos', [])
                                    todos = todos_data

                except:
                    continue

        return {
            'message_count': message_count,
            'todos': todos,
            'last_message': last_message
        }
    except:
        return None

def main():
    """主函数"""
    console.print("[bold blue]🔍 Claude Code Monitor - 测试扫描[/bold blue]\n")

    claude_root = Path.home() / '.claude' / 'projects'

    all_sessions = []
    todo_sessions = []

    # 扫描所有项目
    for project_dir in claude_root.iterdir():
        if project_dir.is_dir():
            project_name = project_dir.name.replace('-Users-haya-', '').replace('-', '/')

            for jsonl_file in project_dir.glob('*.jsonl'):
                session_info = parse_session_file(jsonl_file)
                if session_info:
                    session_data = {
                        'project': project_name,
                        'session_id': jsonl_file.stem[:8] + '...',
                        'file': str(jsonl_file),
                        'messages': session_info['message_count'],
                        'todos': session_info['todos'],
                        'last_msg': session_info['last_message']
                    }
                    all_sessions.append(session_data)

                    if session_info['todos']:
                        todo_sessions.append(session_data)

    # 统计信息
    console.print(Panel(f"""
📊 [bold cyan]统计信息[/bold cyan]
• 总会话数: [bold]{len(all_sessions)}[/bold]
• 包含TodoWrite的会话: [bold]{len(todo_sessions)}[/bold]
• 扫描的项目数: [bold]{len(set(s['project'] for s in all_sessions))}[/bold]
""", title="扫描结果"))

    # 显示TodoWrite会话
    if todo_sessions:
        console.print("\n[bold yellow]📝 包含TodoWrite的会话:[/bold yellow]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("项目", width=30)
        table.add_column("会话ID", width=12)
        table.add_column("消息数", width=8)
        table.add_column("任务数", width=8)
        table.add_column("任务状态", width=40)

        for session in todo_sessions[:20]:  # 只显示前20个
            # 统计任务状态
            stats = defaultdict(int)
            for todo in session['todos']:
                stats[todo.get('status', 'unknown')] += 1

            status_str = f"✅{stats['completed']} 🔄{stats['in_progress']} ⏳{stats['pending']}"

            table.add_row(
                session['project'],
                session['session_id'],
                str(session['messages']),
                str(len(session['todos'])),
                status_str
            )

        console.print(table)

        # 显示最新的TodoWrite内容
        console.print("\n[bold cyan]🎯 最新的TodoWrite任务:[/bold cyan]\n")

        # 找到最新的session
        if todo_sessions:
            latest = todo_sessions[0]
            for i, todo in enumerate(latest['todos'][:5]):
                icon = {'completed': '✅', 'in_progress': '🔄', 'pending': '⏳'}.get(todo.get('status'), '❓')
                console.print(f"{i+1}. {icon} {todo.get('content', '未知任务')}")

if __name__ == "__main__":
    main()