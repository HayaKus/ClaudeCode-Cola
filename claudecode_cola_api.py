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

def pin_session(session_id):
    """标记会话"""
    pinned_sessions = load_pinned_sessions()
    if session_id in pinned_sessions:
        print(f"会话 {session_id} 已经被标记")
        return False
    pinned_sessions.add(session_id)
    save_pinned_sessions(pinned_sessions)
    print(f"会话 {session_id} 已标记")
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
    if pinned_sessions:
        print("已标记的会话:")
        for session_id in sorted(pinned_sessions):
            print(f"  - {session_id}")
    else:
        print("没有已标记的会话")

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