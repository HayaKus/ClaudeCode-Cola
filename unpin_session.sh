#!/bin/bash
# 取消标记ClaudeCode会话

if [ $# -eq 0 ]; then
    echo "用法: $0 <会话ID>"
    echo "示例: $0 f2f5f4ea-489a-44cf-85ff-b20074ebdd06"
    exit 1
fi

SESSION_ID="$1"
python3 claudecode_cola_api.py unpin "$SESSION_ID"