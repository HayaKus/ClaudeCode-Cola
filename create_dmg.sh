#!/bin/bash

# ClaudeCode-Cola DMG 创建脚本

set -e  # 遇到错误立即退出

echo "🥤 开始创建 DMG 安装包..."

# 进入脚本所在目录
cd "$(dirname "$0")"

# 检查应用是否存在
if [ ! -d "dist/ClaudeCode-Cola.app" ]; then
    echo "❌ 应用不存在，请先运行 ./build_app.sh 打包应用"
    exit 1
fi

# 版本号
VERSION="1.0.1"
DMG_NAME="ClaudeCode-Cola-${VERSION}.dmg"

# 清理旧的 DMG
echo "🧹 清理旧的 DMG 文件..."
rm -f "dist/${DMG_NAME}"
rm -rf dist/dmg_temp

# 创建临时目录
echo "📁 创建临时目录..."
mkdir -p dist/dmg_temp

# 复制应用到临时目录
echo "📦 复制应用..."
cp -r "dist/ClaudeCode-Cola.app" dist/dmg_temp/

# 创建应用程序文件夹的符号链接
echo "🔗 创建应用程序文件夹链接..."
ln -s /Applications dist/dmg_temp/Applications

# 创建 DMG
echo "💿 创建 DMG..."
hdiutil create -volname "ClaudeCode-Cola" \
    -srcfolder dist/dmg_temp \
    -ov -format UDZO \
    "dist/${DMG_NAME}"

# 清理临时文件
echo "🧹 清理临时文件..."
rm -rf dist/dmg_temp

# 检查结果
if [ -f "dist/${DMG_NAME}" ]; then
    echo "✅ DMG 创建成功！"
    echo ""
    echo "DMG 位置: dist/${DMG_NAME}"
    echo ""
    echo "📝 下一步："
    echo "1. 测试 DMG: open dist/${DMG_NAME}"
    echo "2. 上传到服务器用于 Homebrew Cask 分发"
    echo "3. 计算 SHA256: shasum -a 256 dist/${DMG_NAME}"
else
    echo "❌ DMG 创建失败"
    exit 1
fi
