# Homebrew Cask 安装配置指南

本文档说明如何配置 Homebrew Cask，让用户可以通过 `brew install --cask` 安装 ClaudeCode-Cola。

## 方案选择

### 推荐方案：使用 GitLab Release

**优点：**
- ✅ 不会让Git仓库变大
- ✅ 版本管理清晰
- ✅ 下载速度快（内网）
- ✅ 符合最佳实践

## 实施步骤

### 第一步：上传 DMG 到 GitLab Release

1. **在GitLab上创建Release**
   - 访问：https://code.alibaba-inc.com/haya.lhw/ClaudeCode-Cola/-/releases
   - 点击"New release"
   - Tag name: `v1.0.0`
   - Release title: `ClaudeCode-Cola v1.0.0`
   - 描述：添加版本说明

2. **上传 DMG 文件**
   - 在Release页面上传 `dist/ClaudeCode-Cola-1.0.0.dmg`
   - 或使用命令行（如果配置了GitLab CLI）

3. **获取下载链接**
   - 上传后会得到类似这样的链接：
   ```
   https://code.alibaba-inc.com/haya.lhw/ClaudeCode-Cola/-/releases/v1.0.0/downloads/ClaudeCode-Cola-1.0.0.dmg
   ```

### 第二步：更新 Homebrew Cask Formula

编辑 `homebrew/claudecode-cola.rb`：

```ruby
cask "claudecode-cola" do
  version "1.0.0"
  sha256 "750144754610c2f7d496853f4979bb31b95fd224bf0ad84b5cd4b64d39f87de5"

  # 替换为实际的GitLab Release下载链接
  url "https://code.alibaba-inc.com/haya.lhw/ClaudeCode-Cola/-/releases/v#{version}/downloads/ClaudeCode-Cola-#{version}.dmg"
  name "ClaudeCode-Cola"
  desc "Monitor Claude Code sessions and TodoWrite tasks"
  homepage "https://code.alibaba-inc.com/haya.lhw/ClaudeCode-Cola"

  livecheck do
    url :homepage
    strategy :github_latest
  end

  app "ClaudeCode-Cola.app"

  zap trash: [
    "~/.claudecode-cola",
  ]
end
```

### 第三步：创建 Homebrew Tap 仓库

**选项A：在当前仓库中提供（简单）**

用户安装命令：
```bash
# 方式1：直接从仓库安装
brew install --cask homebrew/claudecode-cola.rb

# 方式2：添加tap后安装
brew tap haya.lhw/claudecode-cola https://code.alibaba-inc.com/haya.lhw/ClaudeCode-Cola.git
brew install --cask claudecode-cola
```

**选项B：创建独立的Tap仓库（标准）**

1. 创建新仓库：`homebrew-claudecode-cola`
2. 仓库结构：
   ```
   homebrew-claudecode-cola/
   └── Casks/
       └── claudecode-cola.rb
   ```
3. 用户安装：
   ```bash
   brew tap haya.lhw/claudecode-cola
   brew install --cask claudecode-cola
   ```

### 第四步：测试安装

```bash
# 1. 添加tap
brew tap haya.lhw/claudecode-cola https://code.alibaba-inc.com/haya.lhw/ClaudeCode-Cola.git

# 2. 安装
brew install --cask claudecode-cola

# 3. 验证
ls /Applications/ClaudeCode-Cola.app

# 4. 启动
open /Applications/ClaudeCode-Cola.app
```

## 版本更新流程

当发布新版本时：

1. **更新版本号**
   ```bash
   # 修改 setup.py 和 create_dmg.sh 中的版本号
   VERSION="1.1.0"
   ```

2. **重新打包**
   ```bash
   ./build_app.sh
   ./create_dmg.sh
   ```

3. **计算新的SHA256**
   ```bash
   shasum -a 256 dist/ClaudeCode-Cola-1.1.0.dmg
   ```

4. **创建新的GitLab Release**
   - Tag: `v1.1.0`
   - 上传新的DMG

5. **更新Formula**
   ```ruby
   version "1.1.0"
   sha256 "新的哈希值"
   ```

6. **提交更新**
   ```bash
   git add homebrew/claudecode-cola.rb
   git commit -m "Release v1.1.0"
   git push
   ```

## 用户安装文档

在 README.md 中添加：

```markdown
## 安装方式

### 通过 Homebrew 安装（推荐）

\`\`\`bash
# 添加 tap
brew tap haya.lhw/claudecode-cola https://code.alibaba-inc.com/haya.lhw/ClaudeCode-Cola.git

# 安装应用
brew install --cask claudecode-cola
\`\`\`

安装后，应用会出现在"应用程序"文件夹中。

### 手动安装

1. 从 [Releases](https://code.alibaba-inc.com/haya.lhw/ClaudeCode-Cola/-/releases) 下载最新的 DMG 文件
2. 双击打开 DMG
3. 拖拽应用到"应用程序"文件夹
4. 从启动台或访达启动应用
```

## 故障排除

### 问题1：下载失败
- 检查网络连接
- 确认GitLab Release链接可访问
- 验证SHA256是否正确

### 问题2：安装失败
- 检查macOS版本（需要10.14+）
- 查看Homebrew日志：`brew install --cask claudecode-cola --verbose`

### 问题3：应用无法启动
- 检查系统日志：Console.app
- 尝试从终端启动查看错误：
  ```bash
  /Applications/ClaudeCode-Cola.app/Contents/MacOS/ClaudeCode-Cola
  ```

## 注意事项

1. **不要将DMG提交到Git仓库**
   - DMG文件很大（103MB）
   - 会让仓库变得臃肿
   - 使用GitLab Release或OSS存储

2. **保持SHA256准确**
   - 每次更新DMG都要重新计算
   - 不匹配会导致安装失败

3. **版本号一致性**
   - setup.py
   - create_dmg.sh
   - homebrew/claudecode-cola.rb
   - GitLab Release tag

## 参考资料

- [Homebrew Cask 文档](https://docs.brew.sh/Cask-Cookbook)
- [GitLab Release 文档](https://docs.gitlab.com/ee/user/project/releases/)
- [py2app 文档](https://py2app.readthedocs.io/)
