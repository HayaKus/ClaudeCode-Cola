#!/bin/bash

# ClaudeCode-Cola 启动脚本

echo "🥤 启动 ClaudeCode-Cola..."

# 进入脚本所在目录
cd "$(dirname "$0")"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖是否安装
if ! python -c "import PyQt6" 2>/dev/null; then
    echo "📦 正在安装依赖..."
    pip install -r requirements-app.txt
    echo "✅ 依赖安装完成"
fi

# 运行应用
echo "🚀 启动应用..."
python src/main.py

# 退出虚拟环境
deactivate
