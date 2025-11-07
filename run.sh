#!/bin/bash
# Claude Monitor 启动脚本

echo "🚀 启动 Claude Code 监控器..."

# 检查Python版本
if ! python3 --version &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python3"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖包..."
pip install -r requirements.txt -q

# 运行监控器
echo "🎯 启动监控程序..."
python3 claude_monitor.py