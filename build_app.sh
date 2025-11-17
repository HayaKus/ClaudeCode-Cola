#!/bin/bash

# ClaudeCode-Cola 应用打包脚本

set -e  # 遇到错误立即退出

echo "🥤 开始打包 ClaudeCode-Cola..."

# 进入脚本所在目录
cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 ./run.sh 创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 安装 py2app（如果未安装）
if ! python -c "import py2app" 2>/dev/null; then
    echo "📦 安装 py2app..."
    pip install py2app
fi

# 清理之前的构建
echo "🧹 清理旧的构建文件..."
rm -rf build dist

# 开始打包
echo "📦 打包应用..."
python setup.py py2app

# 检查打包结果
if [ -d "dist/ClaudeCode-Cola.app" ]; then
    echo "✅ 打包成功！"
    echo ""
    echo "应用位置: dist/ClaudeCode-Cola.app"
    echo ""
    echo "📝 下一步："
    echo "1. 测试应用: open dist/ClaudeCode-Cola.app"
    echo "2. 安装到应用程序文件夹: cp -r dist/ClaudeCode-Cola.app /Applications/"
    echo "3. 创建 DMG: ./create_dmg.sh"
else
    echo "❌ 打包失败"
    exit 1
fi

# 退出虚拟环境
deactivate
