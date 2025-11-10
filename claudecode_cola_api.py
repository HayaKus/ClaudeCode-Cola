#!/usr/bin/env python3
"""
ClaudeCode-Cola API接口
用于外部命令控制（如标记/取消标记会话）
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# ClaudeCode-Cola配置目录
CONFIG_DIR = Path.home() / '.claudecode-cola'
CONFIG_FILE = CONFIG_DIR / 'pinned_sessions.json'

# Claude项目根目录
CLAUDE_ROOT = Path.home() / '.claude' / 'projects'

def ensure_config_dir():
    """确保配置目录存在"""
    CONFIG_DIR.mkdir(exist_ok=True)

def load_pinned_sessions():
    """加载已标记的会话列表"""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_pinned_sessions(pinned_sessions):
    """保存已标记的会话列表"""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(pinned_sessions), f, ensure_ascii=False, indent=2)

def session_exists(session_id):
    """检查会话是否存在"""
    if not CLAUDE_ROOT.exists():
        return False, None

    # 遍历所有项目目录
    for project_dir in CLAUDE_ROOT.iterdir():
        if project_dir.is_dir():
            session_file = project_dir / f"{session_id}.jsonl"
            if session_file.exists():
                # 获取项目名称
                project_path = project_dir.name
                if project_path.startswith('-'):
                    # 将Claude的路径编码转换为标准路径
                    path_without_prefix = project_path[1:]
                    project_name = '/' + path_without_prefix.replace('-', '/')
                else:
                    project_name = project_path
                return True, project_name
    return False, None

def pin_session(session_id):
    """标记会话"""
    # 首先检查会话是否存在
    exists, project_name = session_exists(session_id)
    if not exists:
        print(f"❌ 错误: 会话 {session_id} 不存在")
        print("   提示: 请确认会话ID是否正确,或者该会话是否已经创建")
        return False

    pinned_sessions = load_pinned_sessions()
    if session_id in pinned_sessions:
        print(f"⚠️  会话 {session_id} 已经被标记")
        print(f"   项目: {project_name}")
        return False

    pinned_sessions.add(session_id)
    save_pinned_sessions(pinned_sessions)
    print(f"✅ 会话 {session_id} 已标记")
    print(f"   项目: {project_name}")
    return True

def unpin_session(session_id):
    """取消标记会话"""
    pinned_sessions = load_pinned_sessions()
    if session_id not in pinned_sessions:
        print(f"会话 {session_id} 未被标记")
        return False
    pinned_sessions.remove(session_id)
    save_pinned_sessions(pinned_sessions)
    print(f"会话 {session_id} 已取消标记")
    return True

def list_pinned_sessions():
    """列出所有已标记的会话"""
    pinned_sessions = load_pinned_sessions()
    if not pinned_sessions:
        print("📭 没有已标记的会话")
        return

    print(f"📌 已标记的会话 (共 {len(pinned_sessions)} 个):")
    print("=" * 80)

    # 为每个标记的会话显示详细信息
    valid_count = 0
    invalid_sessions = []

    for session_id in sorted(pinned_sessions):
        exists, project_name = session_exists(session_id)
        if exists:
            valid_count += 1
            print(f"\n  {valid_count}. 会话ID: {session_id}")
            print(f"     项目: {project_name}")
        else:
            invalid_sessions.append(session_id)

    # 如果有无效的会话，给出提示
    if invalid_sessions:
        print("\n" + "=" * 80)
        print(f"⚠️  发现 {len(invalid_sessions)} 个无效会话(文件已删除):")
        for session_id in invalid_sessions:
            print(f"  - {session_id}")
        print("\n提示: 可以使用 unpin 命令取消标记这些无效会话")

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python claudecode_cola_api.py pin <会话ID>     # 标记会话")
        print("  python claudecode_cola_api.py unpin <会话ID>   # 取消标记会话")
        print("  python claudecode_cola_api.py list            # 列出所有标记的会话")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'pin':
        if len(sys.argv) < 3:
            print("错误: 请提供会话ID")
            sys.exit(1)
        session_id = sys.argv[2]
        pin_session(session_id)
    elif command == 'unpin':
        if len(sys.argv) < 3:
            print("错误: 请提供会话ID")
            sys.exit(1)
        session_id = sys.argv[2]
        unpin_session(session_id)
    elif command == 'list':
        list_pinned_sessions()
    else:
        print(f"错误: 未知命令 '{command}'")
        print("可用命令: pin, unpin, list")
        sys.exit(1)

if __name__ == "__main__":
    main()