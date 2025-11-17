# ClaudeCode-Cola Mac 应用安装指南

## 📋 系统要求

- macOS 10.15 (Catalina) 或更高版本
- Python 3.9 或更高版本
- 至少 500MB 可用磁盘空间

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd /Users/haya/Code/ClaudeCode-Cola

# 创建虚拟环境（如果还没创建）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装应用依赖
pip install -r requirements-app.txt
```

### 2. 运行应用

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 运行应用
python src/main.py
```

应用启动后，你会看到：
- 🖥️ **主窗口**：显示所有 Claude Code 会话
- 🥤 **菜单栏图标**：系统托盘常驻图标

## 📂 配置 Claude Code 项目目录

应用默认监控目录：`~/.claude/projects`（Claude Code 官方默认目录）

如果你的 Claude Code 会话文件在其他位置，可以：

### 方法一：修改配置文件

编辑 `~/.claudecode-cola/config.json`：

```json
{
  "projects_dir": "/your/custom/path/to/projects"
}
```

### 方法二：创建符号链接

```bash
# 将实际的 Claude Code 项目目录链接到默认位置
ln -s /actual/path/to/projects ~/.claude/projects
```

## 🎯 使用指南

### 主窗口功能

1. **会话列表**（左侧）
   - 🟢 绿色圆点：活跃会话
   - 🟡 黄色圆点：不活跃会话
   - 📌 图钉：已标记会话

2. **详情面板**（右侧）
   - 项目路径和会话信息
   - Todo 任务进度条
   - Todo 任务列表详情

3. **搜索功能**
   - 工具栏中的搜索框可以过滤会话

4. **菜单功能**
   - `Cmd+R`：刷新会话列表
   - `Cmd+F`：搜索会话
   - `Cmd+Q`：退出应用

### 系统托盘功能

右键点击托盘图标：
- **显示主窗口**：打开主界面
- **活跃会话**：快速访问活跃会话目录
- **刷新**：手动刷新会话数据
- **退出**：关闭应用

双击托盘图标：快速显示主窗口

## ⚙️ 配置选项

配置文件位置：`~/.claudecode-cola/config.json`

可配置项：

```json
{
  "show_window_on_start": true,      // 启动时显示主窗口
  "theme": "auto",                    // 主题：auto/light/dark
  "auto_refresh": true,               // 自动刷新
  "refresh_interval": 5,              // 刷新间隔（秒）
  "projects_dir": "~/.claude/projects",  // 项目目录
  "enable_notifications": true,       // 启用通知
  "notify_on_error": true,           // 错误时通知
  "notify_on_inactive": false        // 会话不活跃时通知
}
```

## 🐛 常见问题

### 1. 找不到会话文件？

**问题**：应用显示"0 个会话"

**解决方法**：
- 检查 Claude Code 是否在 `~/.claude/projects` 目录下创建了 `.jsonl` 文件
- 确认配置文件中的 `projects_dir` 路径正确
- 手动刷新（`Cmd+R`）
- 确认你已经使用 Claude Code 创建过会话

### 2. 虚拟环境激活失败？

**问题**：运行时提示找不到模块

**解决方法**：
```bash
# 确保先激活虚拟环境
source venv/bin/activate

# 检查是否在正确的环境中
which python
# 应该显示：/Users/haya/Code/ClaudeCode-Cola/venv/bin/python
```

### 3. 应用无法启动？

**问题**：点击运行没有反应

**解决方法**：
```bash
# 在终端运行，查看错误信息
source venv/bin/activate
python src/main.py
```

查看日志文件：`~/.claudecode-cola/logs/app_YYYYMMDD.log`

### 4. 如何重置配置？

```bash
# 删除配置文件，应用会重新创建默认配置
rm ~/.claudecode-cola/config.json
```

## 📝 日志文件

日志位置：`~/.claudecode-cola/logs/`

每天一个日志文件：`app_20251117.log`

查看最新日志：
```bash
tail -f ~/.claudecode-cola/logs/app_$(date +%Y%m%d).log
```

## 🔄 更新应用

```bash
# 拉取最新代码
git pull

# 更新依赖
source venv/bin/activate
pip install -r requirements-app.txt --upgrade

# 重新运行
python src/main.py
```

## 🛠️ 开发模式

如果你想开发或调试应用：

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 代码格式化
black src/

# 类型检查
mypy src/
```

## 📦 打包成独立应用（未来功能）

未来将支持打包成 `.app` 文件，可以直接双击运行：

```bash
# 构建应用（计划中）
python setup.py py2app
```

## 💡 提示

- 应用会自动每 5 秒刷新一次会话数据
- 可以关闭主窗口，应用会继续在托盘运行
- 点击托盘图标的"活跃会话"可以快速在 Finder 中打开项目目录

## 📞 反馈

如有问题或建议，请联系：
- 作者：哈雅
- 工号：263321
