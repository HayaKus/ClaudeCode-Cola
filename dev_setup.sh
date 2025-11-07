#!/bin/bash

# 开发环境快速设置脚本

echo "设置开发环境..."

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 创建数据目录
mkdir -p ~/Code/ClaudeCode-Cola/.claude-code-manager

echo "开发环境设置完成！"
echo ""
echo "运行测试："
echo "  source venv/bin/activate"
echo "  python test_run.py"