#!/bin/bash

# 创建应用图标脚本

set -e

echo "🥤 创建 ClaudeCode-Cola 应用图标..."

# 创建临时目录
mkdir -p temp_icon

# 使用 Python 创建一个简单的可乐图标
python3 << 'EOF'
from PIL import Image, ImageDraw, ImageFont
import os

# 创建 1024x1024 的图像
size = 1024
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 绘制圆形背景（红色）
margin = 50
draw.ellipse([margin, margin, size-margin, size-margin], fill='#DC143C')

# 绘制可乐emoji（使用大字体）
try:
    # 尝试使用系统字体
    font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 700)
except:
    # 如果失败，使用默认字体
    font = ImageFont.load_default()

# 绘制🥤emoji
text = "🥤"
# 获取文本边界框
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# 居中绘制
x = (size - text_width) // 2
y = (size - text_height) // 2 - 50

draw.text((x, y), text, font=font, embedded_color=True)

# 保存为PNG
img.save('temp_icon/icon_1024.png')
print("✅ 创建了 1024x1024 图标")
EOF

# 检查是否成功创建
if [ ! -f "temp_icon/icon_1024.png" ]; then
    echo "❌ 图标创建失败"
    exit 1
fi

# 创建 iconset 目录
mkdir -p temp_icon/app_icon.iconset

# 生成不同尺寸的图标
echo "📐 生成不同尺寸的图标..."
sips -z 16 16     temp_icon/icon_1024.png --out temp_icon/app_icon.iconset/icon_16x16.png
sips -z 32 32     temp_icon/icon_1024.png --out temp_icon/app_icon.iconset/icon_16x16@2x.png
sips -z 32 32     temp_icon/icon_1024.png --out temp_icon/app_icon.iconset/icon_32x32.png
sips -z 64 64     temp_icon/icon_1024.png --out temp_icon/app_icon.iconset/icon_32x32@2x.png
sips -z 128 128   temp_icon/icon_1024.png --out temp_icon/app_icon.iconset/icon_128x128.png
sips -z 256 256   temp_icon/icon_1024.png --out temp_icon/app_icon.iconset/icon_128x128@2x.png
sips -z 256 256   temp_icon/icon_1024.png --out temp_icon/app_icon.iconset/icon_256x256.png
sips -z 512 512   temp_icon/icon_1024.png --out temp_icon/app_icon.iconset/icon_256x256@2x.png
sips -z 512 512   temp_icon/icon_1024.png --out temp_icon/app_icon.iconset/icon_512x512.png
sips -z 1024 1024 temp_icon/icon_1024.png --out temp_icon/app_icon.iconset/icon_512x512@2x.png

# 转换为 icns
echo "🔄 转换为 .icns 格式..."
iconutil -c icns temp_icon/app_icon.iconset -o temp_icon/app_icon.icns

# 创建目标目录
mkdir -p resources/icons

# 复制到目标位置
cp temp_icon/app_icon.icns resources/icons/app_icon.icns

# 清理临时文件
echo "🧹 清理临时文件..."
rm -rf temp_icon

echo "✅ 应用图标创建成功！"
echo "📍 图标位置: resources/icons/app_icon.icns"
