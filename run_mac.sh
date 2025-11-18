#!/bin/bash
# ClaudeCode-Cola Mac GUI 应用启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    echo "请先安装 Python 3"
    exit 1
fi

# 检查依赖
if [ ! -d "venv" ]; then
    echo "⚠️  未找到虚拟环境，正在创建..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 安装依赖..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 启动 Mac GUI 应用
echo "🥤 启动 ClaudeCode-Cola Mac 应用..."
python3 src/main.py
