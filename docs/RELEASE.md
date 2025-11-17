# ClaudeCode-Cola 发布指南

本文档说明如何打包和发布 ClaudeCode-Cola Mac 应用。

## 前置要求

- macOS 10.14 或更高版本
- Python 3.8+
- 已安装项目依赖（运行过 `./run.sh`）

## 打包流程

### 1. 准备应用图标

应用图标应该是 `.icns` 格式，放在 `resources/icons/app_icon.icns`。

**创建图标的方法：**

```bash
# 如果你有 PNG 图标（建议 1024x1024）
# 1. 创建 iconset 目录
mkdir app_icon.iconset

# 2. 生成不同尺寸的图标
sips -z 16 16     icon.png --out app_icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out app_icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out app_icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out app_icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out app_icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out app_icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out app_icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out app_icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out app_icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out app_icon.iconset/icon_512x512@2x.png

# 3. 转换为 icns
iconutil -c icns app_icon.iconset -o resources/icons/app_icon.icns

# 4. 清理
rm -rf app_icon.iconset
```

**临时方案：** 如果暂时没有图标，可以注释掉 `setup.py` 中的 `iconfile` 行。

### 2. 打包应用

```bash
# 打包成 .app 应用
./build_app.sh
```

这会在 `dist/` 目录下生成 `ClaudeCode-Cola.app`。

### 3. 测试应用

```bash
# 测试打包的应用
open dist/ClaudeCode-Cola.app
```

确保应用能正常启动和运行。

### 4. 创建 DMG 安装包

```bash
# 创建 DMG
./create_dmg.sh
```

这会在 `dist/` 目录下生成 `ClaudeCode-Cola-1.0.0.dmg`。

### 5. 计算 SHA256

```bash
# 计算 DMG 的 SHA256 哈希值
shasum -a 256 dist/ClaudeCode-Cola-1.0.0.dmg
```

记录这个哈希值，后面配置 Homebrew Cask 时需要用到。

## Homebrew Cask 发布

### 1. 上传 DMG

将 `dist/ClaudeCode-Cola-1.0.0.dmg` 上传到可访问的服务器。

**内网选项：**
- 阿里云 OSS
- 内网文件服务器
- GitLab Release Assets

### 2. 更新 Cask Formula

编辑 `homebrew/claudecode-cola.rb`：

```ruby
cask "claudecode-cola" do
  version "1.0.0"
  sha256 "YOUR_SHA256_HERE"  # 替换为实际的 SHA256

  url "https://your-server.com/ClaudeCode-Cola-#{version}.dmg"  # 替换为实际的下载地址
  name "ClaudeCode-Cola"
  desc "Monitor Claude Code sessions and TodoWrite tasks"
  homepage "https://github.com/your-org/ClaudeCode-Cola"  # 替换为实际的项目地址

  app "ClaudeCode-Cola.app"

  zap trash: [
    "~/.claudecode-cola",
  ]
end
```

### 3. 创建 Homebrew Tap

```bash
# 创建一个新的 Git 仓库作为 Homebrew Tap
# 仓库名称格式：homebrew-<tap-name>
# 例如：homebrew-claudecode-cola

# 在仓库中创建 Casks 目录
mkdir -p Casks

# 复制 formula
cp homebrew/claudecode-cola.rb Casks/

# 提交并推送
git add Casks/claudecode-cola.rb
git commit -m "Add ClaudeCode-Cola cask"
git push
```

### 4. 用户安装方式

用户可以通过以下命令安装：

```bash
# 添加你的 tap
brew tap your-org/claudecode-cola

# 安装应用
brew install --cask claudecode-cola
```

## 版本更新

更新版本时：

1. 修改 `setup.py` 中的版本号
2. 修改 `create_dmg.sh` 中的 `VERSION` 变量
3. 重新打包：`./build_app.sh && ./create_dmg.sh`
4. 上传新的 DMG
5. 更新 Homebrew Cask formula 中的版本号和 SHA256
6. 提交更新到 Homebrew Tap 仓库

## 开发模式

开发时无需打包，直接使用：

```bash
./run.sh
```

这会启动开发版本，方便调试和测试。

## 故障排除

### 打包失败

1. 确保虚拟环境已创建：`./run.sh`
2. 确保所有依赖已安装：`pip install -r requirements-app.txt`
3. 检查 Python 版本：`python --version`（需要 3.8+）

### 应用无法启动

1. 检查系统日志：Console.app
2. 尝试从终端启动查看错误：`dist/ClaudeCode-Cola.app/Contents/MacOS/ClaudeCode-Cola`

### DMG 创建失败

1. 确保应用已打包：`ls dist/ClaudeCode-Cola.app`
2. 检查磁盘空间
3. 检查 hdiutil 命令是否可用

## 参考资料

- [py2app 文档](https://py2app.readthedocs.io/)
- [Homebrew Cask 文档](https://docs.brew.sh/Cask-Cookbook)
- [macOS 应用打包指南](https://developer.apple.com/documentation/bundleresources)
