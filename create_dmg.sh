#!/bin/bash

# ClaudeCode-Cola DMG 创建脚本

set -e  # 遇到错误立即退出

echo "🥤 开始创建 DMG 安装包..."

# 进入脚本所在目录
cd "$(dirname "$0")"

# 检查应用是否存在
if [ ! -d "dist/ClaudeCode-Cola.app" ]; then
    echo "❌ 应用不存在,请先运行 ./build_app.sh 打包应用"
    exit 1
fi

# 检查图标文件是否存在
if [ ! -f "resources/icons/app_icon.icns" ]; then
    echo "❌ 图标文件不存在: resources/icons/app_icon.icns"
    exit 1
fi

# 版本号
VERSION="1.0.3"
DMG_NAME="ClaudeCode-Cola-${VERSION}.dmg"
TEMP_DMG="dist/temp_${DMG_NAME}"

# 清理旧的 DMG
echo "🧹 清理旧的 DMG 文件..."
rm -f "dist/${DMG_NAME}"
rm -f "${TEMP_DMG}"
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

# 创建临时可读写的 DMG
echo "💿 创建临时 DMG..."
hdiutil create -volname "ClaudeCode-Cola" \
    -srcfolder dist/dmg_temp \
    -ov -format UDRW \
    "${TEMP_DMG}"

# 挂载 DMG
echo "📌 挂载 DMG..."
MOUNT_OUTPUT=$(hdiutil attach -readwrite -noverify -noautoopen "${TEMP_DMG}" 2>&1)
MOUNT_DIR=$(echo "$MOUNT_OUTPUT" | grep "/Volumes/" | sed 's/.*\(\/Volumes\/.*\)/\1/')

if [ -z "$MOUNT_DIR" ]; then
    echo "❌ 无法挂载 DMG"
    echo "挂载输出: $MOUNT_OUTPUT"
    exit 1
fi

echo "挂载点: $MOUNT_DIR"

# 设置 DMG 卷的图标
echo "🎨 设置 DMG 卷图标..."
# 复制图标到卷的根目录(隐藏文件)
cp "resources/icons/app_icon.icns" "$MOUNT_DIR/.VolumeIcon.icns"

# 使用 SetFile 设置卷图标(需要 Xcode Command Line Tools)
if command -v SetFile &> /dev/null; then
    SetFile -c icnC "$MOUNT_DIR/.VolumeIcon.icns"
    SetFile -a C "$MOUNT_DIR"
else
    echo "⚠️  警告: SetFile 命令不可用,图标可能无法正确显示"
    echo "   请安装 Xcode Command Line Tools: xcode-select --install"
fi

# 卸载 DMG
echo "📤 卸载 DMG..."
hdiutil detach "$MOUNT_DIR"

# 转换为压缩的只读 DMG
echo "🗜️  压缩 DMG..."
hdiutil convert "${TEMP_DMG}" \
    -format UDZO \
    -o "dist/${DMG_NAME}"

# 清理临时文件
echo "🧹 清理临时文件..."
rm -f "${TEMP_DMG}"
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
