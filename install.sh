#!/bin/bash

# ClaudeCode-Cola 安装脚本
# 自动下载并安装应用

set -e

echo "🥤 ClaudeCode-Cola 安装程序"
echo "================================"
echo ""

# 检查是否在macOS上运行
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 错误：此脚本仅支持 macOS"
    exit 1
fi

# 定义变量
DMG_URL="https://code.alibaba-inc.com/haya.lhw/ClaudeCode-Cola/-/raw/master/dist/ClaudeCode-Cola-1.0.0.dmg"
DMG_FILE="/tmp/ClaudeCode-Cola-1.0.0.dmg"
APP_NAME="ClaudeCode-Cola"

echo "📥 正在下载 ${APP_NAME}..."
if command -v curl &> /dev/null; then
    curl -L -o "$DMG_FILE" "$DMG_URL"
elif command -v wget &> /dev/null; then
    wget -O "$DMG_FILE" "$DMG_URL"
else
    echo "❌ 错误：需要 curl 或 wget 来下载文件"
    exit 1
fi

echo "✅ 下载完成"
echo ""

echo "💿 正在挂载 DMG..."
MOUNT_POINT=$(hdiutil attach "$DMG_FILE" | grep Volumes | awk '{print $3}')

if [ -z "$MOUNT_POINT" ]; then
    echo "❌ 错误：无法挂载 DMG 文件"
    exit 1
fi

echo "✅ DMG 已挂载到: $MOUNT_POINT"
echo ""

echo "📦 正在安装应用到 /Applications..."
if [ -d "/Applications/${APP_NAME}.app" ]; then
    echo "⚠️  检测到已存在的应用，正在删除..."
    rm -rf "/Applications/${APP_NAME}.app"
fi

cp -R "${MOUNT_POINT}/${APP_NAME}.app" /Applications/

echo "✅ 应用已安装"
echo ""

echo "🧹 正在清理..."
hdiutil detach "$MOUNT_POINT" -quiet
rm -f "$DMG_FILE"

echo "✅ 清理完成"
echo ""

echo "🎉 安装成功！"
echo ""
echo "启动方式："
echo "  1. 从启动台找到 ${APP_NAME}"
echo "  2. 从访达的应用程序文件夹启动"
echo "  3. 使用命令：open -a ${APP_NAME}"
echo ""
echo "如需卸载，请运行："
echo "  rm -rf /Applications/${APP_NAME}.app"
