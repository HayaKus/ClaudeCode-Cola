# Claude Code Manager 设计文档

## 项目概述

Claude Code Manager 是一个专为 macOS + iTerm2 环境设计的终端工具，用于集中管理和监控所有 Claude Code 会话。它解决了在多任务场景下管理多个独立 Claude Code 会话的困难，特别是在意外关闭终端后难以找回特定会话的问题。

## 核心需求

### 背景问题
- 用户为每个独立任务开启独立的 Claude Code 会话
- 意外关闭终端后，难以在数百个历史记录中找回特定会话
- 缺乏对所有活跃会话的统一视图
- 无法实时查看各会话的 TodoWrite 进度

### 目标用户
- macOS 用户
- 使用 iTerm2 作为终端
- 需要同时管理多个 Claude Code 会话的开发者

## 功能设计

### 1. 会话监控与展示

#### 1.1 实时监控
- 自动发现所有运行中的 Claude Code 进程
- 定期刷新（每 5 秒）
- 显示会话状态：运行中、已暂停、已结束

#### 1.2 会话信息展示
每个会话显示以下信息：
- **工作目录**：会话所在的项目路径
- **会话 ID**：Claude Code 的唯一标识
- **启动时间**：会话创建的时间
- **运行时长**：从启动到现在的时间
- **TodoWrite 进度**：已完成/总任务数及完成百分比
- **最后活跃时间**：最后一次检测到活动的时间

#### 1.3 会话分类
- **活跃会话**：当前正在运行的会话
- **最近关闭**：最近 24 小时内关闭的会话（保留最近 20 个）
- **历史会话**：所有历史会话记录（可搜索）

### 2. 会话管理功能

#### 2.1 新建会话
- 选择或输入工作目录
- 可选：预设会话名称
- 可选：添加会话标签（如 "API开发"、"Bug修复" 等）
- 在新的 iTerm2 窗口中启动 Claude Code

#### 2.2 恢复会话
- 从已关闭会话列表中选择
- 自动执行 `claude -r <session-id>`
- 在新的 iTerm2 窗口中恢复
- 恢复后自动更新会话状态

#### 2.3 附加到会话
- 为运行中的会话打开新的查看窗口
- 不影响原会话的运行
- 用于查看会话输出或并行操作

#### 2.4 会话操作
- **标记重要**：星标重要会话
- **添加备注**：为会话添加说明文字
- **导出日志**：导出会话的完整日志
- **终止会话**：安全结束选中的会话

### 3. 数据持久化

#### 3.1 本地数据库（SQLite）
```sql
-- 会话表
sessions (
    id TEXT PRIMARY KEY,           -- Claude Code 会话 ID
    work_dir TEXT,                 -- 工作目录
    name TEXT,                     -- 自定义名称
    tags TEXT,                     -- 标签（JSON 数组）
    notes TEXT,                    -- 备注
    created_at TIMESTAMP,          -- 创建时间
    closed_at TIMESTAMP,           -- 关闭时间
    last_active TIMESTAMP,         -- 最后活跃时间
    is_starred BOOLEAN,            -- 是否标记为重要
    process_info TEXT              -- 进程信息（JSON）
)

-- TodoWrite 进度表
todo_progress (
    session_id TEXT,               -- 关联会话 ID
    total_todos INTEGER,           -- 总任务数
    completed_todos INTEGER,       -- 已完成数
    todo_list TEXT,                -- 任务列表（JSON）
    updated_at TIMESTAMP,          -- 更新时间
    FOREIGN KEY (session_id) REFERENCES sessions(id)
)

-- Manager 状态表
manager_state (
    key TEXT PRIMARY KEY,          -- 配置键
    value TEXT,                    -- 配置值
    updated_at TIMESTAMP           -- 更新时间
)
```

#### 3.2 日志管理
- 会话输出日志存储在 `~/.claude-code-manager/logs/`
- 按会话 ID 和日期组织
- 自动压缩超过 7 天的日志
- 提供日志搜索功能

### 4. 用户界面设计

#### 4.1 主界面布局
```
╔══════════════════════════════════════════════════════════════════════╗
║                      Claude Code Manager v1.0                         ║
║                    [已连接守护进程] 自动刷新: 开启                    ║
╠══════════════════════════════════════════════════════════════════════╣
║ 🟢 活跃会话 (3)                                                      ║
║                                                                      ║
║ ⭐ [1] ~/projects/web-app                              API重构       ║
║     ID: abc123def | ⏱️ 运行 2h 15m | 📝 Todos: 5/8 (62%)          ║
║     最后活跃: 2 分钟前                                               ║
║                                                                      ║
║   [2] ~/projects/api-service                          Bug修复       ║
║     ID: 456ghi789 | ⏱️ 运行 30m | 📝 Todos: 3/3 (100%) ✅         ║
║     最后活跃: 刚刚                                                   ║
║                                                                      ║
║   [3] ~/documents/report                                            ║
║     ID: 789jkl012 | ⏱️ 运行 5m | 📝 No todos                      ║
║     最后活跃: 1 分钟前                                               ║
║                                                                      ║
╟──────────────────────────────────────────────────────────────────────╢
║ 🔴 最近关闭 (2)                                       [查看全部...]  ║
║                                                                      ║
║   [4] ~/projects/mobile-app                          功能开发       ║
║     ID: 012mno345 | 🕐 1小时前关闭 | 📝 Todos: 10/10 (100%)       ║
║     运行时长: 3h 45m                                                 ║
║                                                                      ║
╟──────────────────────────────────────────────────────────────────────╢
║ 快捷操作:                                                            ║
║ [N] 新建  [R] 恢复  [A] 附加  [S] 搜索  [T] 标签  [H] 帮助  [Q] 退出║
╚══════════════════════════════════════════════════════════════════════╝

选择会话编号或操作: _
```

#### 4.2 新建会话界面
```
╔══════════════════════════════════════════════════════════════════════╗
║                           新建 Claude Code 会话                       ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  工作目录: ~/____________________________________________           ║
║           [Tab: 自动补全] [Enter: 浏览]                              ║
║                                                                      ║
║  会话名称: ____________________________________________ (可选)      ║
║                                                                      ║
║  标签: [ ] API开发  [ ] Bug修复  [ ] 文档  [ ] 测试  [ ] 其他      ║
║                                                                      ║
║  最近使用的目录:                                                     ║
║    1. ~/projects/web-app                                            ║
║    2. ~/projects/api-service                                        ║
║    3. ~/documents/report                                            ║
║                                                                      ║
║  [创建] [取消]                                                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

#### 4.3 会话详情界面
```
╔══════════════════════════════════════════════════════════════════════╗
║                           会话详情                                    ║
╠══════════════════════════════════════════════════════════════════════╣
║  ID: abc123def456ghi                                                 ║
║  目录: ~/projects/web-app                                           ║
║  名称: API重构                                                       ║
║  标签: API开发, 重构                                                 ║
║                                                                      ║
║  创建时间: 2024-01-15 10:30:00                                      ║
║  运行时长: 2小时 15分钟                                              ║
║  状态: 🟢 运行中                                                     ║
║                                                                      ║
║  TodoWrite 进度:                                                     ║
║  ┌─────────────────────────────────────────────────┐               ║
║  │ ✅ 设置项目结构                                   │               ║
║  │ ✅ 创建 API 路由                                  │               ║
║  │ ✅ 实现用户认证                                   │               ║
║  │ ✅ 添加数据库模型                                 │               ║
║  │ ✅ 编写单元测试                                   │               ║
║  │ ⏳ 实现缓存层                                     │               ║
║  │ ⏳ 添加日志系统                                   │               ║
║  │ ⏳ 部署配置                                       │               ║
║  └─────────────────────────────────────────────────┘               ║
║                                                                      ║
║  备注: _________________________________________________________    ║
║                                                                      ║
║  [A] 附加到会话  [E] 导出日志  [T] 终止会话  [返回]                ║
╚══════════════════════════════════════════════════════════════════════╝
```

### 5. 守护进程设计

#### 5.1 架构设计
- Manager 核心作为守护进程运行
- UI 客户端通过 Unix Socket 与守护进程通信
- 守护进程负责：
  - 监控 Claude Code 进程
  - 更新数据库
  - 管理日志文件
  - 处理 iTerm2 操作

#### 5.2 通信协议
```python
# 请求格式
{
    "action": "list_sessions" | "new_session" | "restore_session" | ...,
    "params": {...}
}

# 响应格式
{
    "status": "ok" | "error",
    "data": {...},
    "error": "错误信息（如果有）"
}
```

### 6. iTerm2 集成

#### 6.1 AppleScript 操作
```applescript
-- 创建新窗口并运行命令
tell application "iTerm"
    create window with default profile
    tell current session of current window
        write text "cd ~/projects/web-app && claude"
    end tell
end tell

-- 恢复会话
tell application "iTerm"
    create window with default profile
    tell current session of current window
        write text "claude -r abc123def456"
    end tell
end tell
```

#### 6.2 窗口管理
- 自动设置窗口标题包含会话信息
- 可选：自动排列窗口位置
- 记录窗口 ID 以便后续操作

### 7. 快速恢复机制

#### 7.1 命令行别名
```bash
# ~/.zshrc 配置
alias ccm="/usr/local/bin/claude-code-manager"
alias ccm-daemon="/usr/local/bin/claude-code-manager --daemon"
alias ccm-status="/usr/local/bin/claude-code-manager --status"
alias ccm-stop="/usr/local/bin/claude-code-manager --stop"
```

#### 7.2 自启动配置
```xml
<!-- ~/Library/LaunchAgents/com.claude-code-manager.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claude-code-manager</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/claude-code-manager</string>
        <string>--daemon</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

### 8. 错误处理与恢复

#### 8.1 进程监控异常
- Claude Code 进程意外终止：标记为 "异常关闭"
- 无法获取进程信息：重试机制（最多 3 次）
- 数据库连接失败：使用内存缓存，定期重试

#### 8.2 Manager 崩溃恢复
- 守护进程崩溃：LaunchAgent 自动重启
- UI 崩溃：不影响守护进程，重新连接即可
- 数据完整性：事务性写入，定期备份

## 技术栈

### 开发语言
- **Python 3.9+**：主程序开发
- **SQLite 3**：本地数据存储
- **AppleScript**：iTerm2 控制

### 主要依赖
- `psutil`：进程监控
- `rich`：终端 UI 渲染
- `watchdog`：文件系统监控
- `click`：命令行接口
- `aiosqlite`：异步数据库操作

### 开发工具
- `pytest`：单元测试
- `black`：代码格式化
- `pylint`：代码检查

## 安装与使用

### 安装步骤
```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/claude-code-manager.git
cd claude-code-manager

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装到系统
python setup.py install

# 4. 配置自启动（可选）
ccm --install-daemon
```

### 基本使用
```bash
# 启动 Manager
ccm

# 查看守护进程状态
ccm --status

# 停止守护进程
ccm --stop

# 查看帮助
ccm --help
```

## 未来扩展

### 第一阶段增强
1. **会话分组**：按项目或标签分组显示
2. **搜索过滤**：支持按目录、标签、时间等过滤
3. **批量操作**：批量关闭、导出等
4. **统计分析**：会话使用时长统计、TodoWrite 完成率分析

### 第二阶段增强
1. **Web 界面**：提供 Web UI 替代方案
2. **远程管理**：支持 SSH 远程管理会话
3. **团队协作**：共享会话状态、进度同步
4. **插件系统**：支持自定义扩展

### 第三阶段增强
1. **AI 辅助**：基于历史数据的智能建议
2. **自动化**：会话模板、自动化工作流
3. **集成其他工具**：VS Code、Git 等集成
4. **跨平台支持**：支持 Linux、Windows

## 总结

Claude Code Manager 旨在提供一个简单、高效、可靠的会话管理解决方案。通过集中化的管理界面和智能的会话追踪，让开发者能够更专注于任务本身，而不必担心会话丢失或管理混乱的问题。