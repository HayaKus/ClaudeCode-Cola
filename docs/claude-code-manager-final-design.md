# Claude Code Manager (ClaudeCode-Cola) 最终设计文档

## 1. 项目概述

### 1.1 项目简介
Claude Code Manager (ClaudeCode-Cola) 是一个专为 macOS + iTerm2 环境设计的智能会话管理工具。项目名称 ClaudeCode-Cola 是 Coca-Cola 的谐音，寓意像可乐一样让人精神焕发、提高工作效率。

### 1.2 核心价值
- **集中管理**：统一管理所有 Claude Code 会话，一目了然
- **智能助手**：集成 Claude AI 助手，提供智能化的会话管理体验
- **防止丢失**：再也不用担心意外关闭终端后找不到会话
- **效率提升**：会话模板、性能监控、智能通知等功能大幅提升工作效率

### 1.3 目标用户
- macOS 用户
- 使用 iTerm2 作为主要终端
- 需要同时管理多个 Claude Code 会话的开发者

## 2. 核心功能详解

### 2.1 会话监控与展示

#### 2.1.1 实时会话发现
- 自动扫描系统中所有运行的 Claude Code 进程
- 每 5 秒刷新一次（可配置）
- 智能识别会话状态：运行中、暂停、已结束、异常退出

#### 2.1.2 会话信息展示
每个会话展示以下关键信息：

1. **会话名称**（最重要）
   - Manager 创建的会话：必须指定有意义的名称
   - 外部创建的会话：显示为"未命名-<会话ID前6位>"，可后续补充名称

2. **基础信息**
   - 工作目录：会话所在的项目路径
   - 会话 ID：Claude Code 的唯一标识
   - iTerm2 窗口标题：`[CCCL] <会话名称> - <会话ID>`

3. **时间信息**
   - 启动时间：会话创建的时间
   - 运行时长：从启动到现在的时间
   - 最后活跃：最后一次检测到活动的时间

4. **性能指标**
   - CPU 使用率：实时监控
   - 内存占用：以 MB 为单位
   - 活跃状态：闲置时间提示

5. **任务进度**
   - TodoWrite 总任务数和已完成数
   - 完成百分比
   - 当前正在进行的任务

#### 2.1.3 会话分类
- **活跃会话**：当前正在运行的所有会话
- **最近关闭**：24小时内关闭的会话（保留最近20个）
- **历史记录**：所有历史会话（支持搜索和筛选）

### 2.2 会话管理功能

#### 2.2.1 创建新会话
```
步骤：
1. 选择或输入工作目录
2. 设置会话名称（必填）
3. 选择标签（可选）：API开发、Bug修复、文档编写等
4. 选择会话模板（可选）
5. 系统自动：
   - 打开新的 iTerm2 窗口
   - 设置窗口标题为 [CCCL] <会话名称> - <会话ID>
   - 执行 claude code --dangerously-skip-permissions
   - 记录会话信息
```

#### 2.2.2 恢复会话
- 从已关闭会话列表选择
- 自动执行 `claude -r <session-id>`
- 恢复窗口标题
- 更新会话状态

#### 2.2.3 会话操作
- **标记重要**：星标重要会话，优先显示
- **添加备注**：记录会话相关的重要信息
- **导出日志**：导出完整的会话日志
- **终止会话**：安全关闭选中的会话
- **保存为模板**：将当前配置保存为可复用模板

### 2.3 会话模板系统

#### 2.3.1 预设模板
```json
{
  "前端开发": {
    "work_dir": "~/projects/frontend",
    "name_pattern": "前端-{feature}-{date}",
    "tags": ["前端", "React"],
    "default_todos": [
      "创建组件结构",
      "实现业务逻辑",
      "添加样式",
      "编写单元测试",
      "更新文档"
    ]
  }
}
```

#### 2.3.2 自定义模板
- 用户可保存自己的常用配置
- 支持变量替换：{date}、{time}、{feature}
- 可预设 TodoWrite 任务列表

### 2.4 性能监控系统

#### 2.4.1 实时监控指标
- **CPU 使用率**：通过 ps 命令获取，每10秒更新
- **内存占用**：显示实际使用的内存量
- **闲置时间**：检测最后一次活动时间

#### 2.4.2 异常状态标记
- 🔴 **异常退出**：进程意外终止
- ⚠️ **长时间未活动**：超过30分钟无操作
- 🔥 **高资源占用**：CPU使用率超过80%
- ✅ **任务已完成**：TodoWrite 100%完成

#### 2.4.3 智能提醒
- 检测到异常状态时自动通知
- 可配置提醒阈值

### 2.5 通知系统

#### 2.5.1 通知类型
1. **任务进度通知**
   - TodoWrite 任务全部完成
   - 达到重要里程碑（如50%、75%）

2. **会话状态通知**
   - 会话异常退出
   - 长时间未活动提醒
   - 高资源占用警告

#### 2.5.2 通知实现
```applescript
-- 通过 iTerm2 发送系统通知
tell application "iTerm"
    display notification "API重构任务已完成！"
        with title "Claude Code Manager"
        subtitle "会话: API重构"
        sound name "Glass"
end tell
```

### 2.6 智能助手集成

#### 2.6.1 助手能力
1. **会话分析**
   - 分析当前工作状态
   - 识别可以关闭的会话
   - 提供效率建议

2. **自动化操作**
   - 批量管理会话
   - 智能创建会话
   - 执行复杂操作

3. **数据洞察**
   - 工作效率统计
   - 时间分布分析
   - 任务完成率趋势

#### 2.6.2 交互方式
- 自然语言对话
- 上下文理解
- 主动建议

## 3. 技术架构

### 3.1 系统架构
```
┌─────────────────────────────────────────┐
│      Terminal UI (Rich + Claude AI)      │
│         实时刷新 + 智能交互              │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│          Core Manager (Python)           │
│  ├─ 进程监控 (psutil)                   │
│  ├─ iTerm2 控制 (AppleScript)           │
│  ├─ Claude API 集成                     │
│  └─ 数据管理 (JSON)                     │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Local Storage (JSON)              │
│  ~/Code/ClaudeCode-Cola/                 │
│  └─ .claude-code-manager/               │
│     ├─ sessions.json                    │
│     ├─ config.json                      │
│     ├─ templates.json                   │
│     └─ logs/                           │
└─────────────────────────────────────────┘
```

### 3.2 数据存储

#### 3.2.1 目录结构
```
~/Code/ClaudeCode-Cola/.claude-code-manager/
├── sessions.json      # 会话信息
├── config.json        # 用户配置
├── templates.json     # 会话模板
├── assistant/         # 助手上下文
│   └── context.json
└── logs/             # 会话日志
    └── <session-id>/
        └── <date>.log
```

#### 3.2.2 数据格式

**sessions.json**
```json
{
  "active_sessions": {
    "abc123": {
      "id": "abc123",
      "name": "API重构",
      "work_dir": "~/projects/web-app",
      "created_at": "2024-01-15T10:30:00",
      "last_active": "2024-01-15T12:45:00",
      "is_starred": true,
      "tags": ["API开发", "重构"],
      "notes": "重构用户认证模块",
      "process_info": {
        "pid": 12345,
        "iTerm_window_id": "window-1",
        "iTerm_window_title": "[CCCL] API重构 - abc123"
      },
      "performance": {
        "cpu_percent": 12.5,
        "memory_mb": 256,
        "inactive_minutes": 0
      },
      "todo_progress": {
        "total": 8,
        "completed": 5,
        "current_task": "实现缓存层",
        "last_completed_at": "2024-01-15T12:30:00"
      }
    }
  },
  "closed_sessions": [...],
  "templates": [...]
}
```

**config.json**
```json
{
  "claude_api": {
    "base_url": "https://api.anthropic.com",
    "api_key": "sk-ant-...",
    "model_name": "claude-3-opus-20240229"
  },
  "general": {
    "default_work_dir": "~/projects",
    "log_retention_days": 30,
    "auto_refresh": true,
    "refresh_interval": 5
  },
  "performance": {
    "inactive_threshold_minutes": 30,
    "high_cpu_threshold": 80,
    "monitor_interval": 10
  },
  "notifications": {
    "enabled": true,
    "level": "important",
    "todo_complete": true,
    "session_inactive": true,
    "session_crashed": true,
    "high_resource_usage": true
  }
}
```

## 4. 用户界面设计

### 4.1 主界面
```
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                      Claude Code Manager v1.0 - 你的智能会话管家                          ║
╠═════════════════════════════════════════════════════════════════════════════════╤════════╣
║ 🟢 活跃会话 (3)                                                                 │ AI助手 ║
║                                                                                │        ║
║ ⭐ [1] API重构 - ~/projects/web-app                                            │ 哈雅， ║
║     ID: abc123 | ⏱️ 2h 15m | 💻 CPU: 12% MEM: 256MB                          │ 我看到 ║
║     📝 5/8 (62%) | 当前: 实现缓存层                                            │ 你有3个║
║                                                                                │ 活跃的 ║
║   [2] Bug修复 - ~/projects/api-service                                        │ 会话。 ║
║     ID: def456 | ⏱️ 30m | 💻 CPU: 5% MEM: 128MB                              │        ║
║     📝 3/3 (100%) ✅ | 已完成，建议关闭                                        │ API重构║
║                                                                                │ 进度62%║
║ ⚠️ [3] 数据分析 - ~/documents/report                                           │ 进展不 ║
║     ID: ghi789 | ⏱️ 45m | 💻 CPU: 0% MEM: 64MB                               │ 错。   ║
║     📝 未设置任务 | 已闲置 35 分钟                                             │        ║
║                                                                                │ Bug修复║
║ 🔴 最近关闭 (2)                                                  [查看更多...] │ 已完成,║
║                                                                                │ 可以关 ║
║   [4] 数据库迁移 - ~/projects/database              1小时前 | 3h 45m          │ 闭了。 ║
║   [5] 前端优化 - ~/projects/frontend                3小时前 | 2h 30m          │        ║
║                                                                                │ 需要我 ║
╟────────────────────────────────────────────────────────────────────────────────┤ 帮你： ║
║ 💬 与助手对话:                                                                  │ 1.关闭 ║
║ > 帮我关闭已完成的会话，并创建一个新的数据库优化会话_                            │ 2.分析 ║
║                                                                                │ 3.创建 ║
║ [Enter] 发送  [N] 新建  [T] 模板  [S] 设置  [H] 帮助  [Q] 退出               │        ║
╚═════════════════════════════════════════════════════════════════════════════════╧════════╝
```

### 4.2 会话创建界面
```
╔══════════════════════════════════════════════════════════════════════╗
║                         创建新的 Claude Code 会话                     ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  会话名称: API接口开发___________________________________________ ✓  ║
║                                                                      ║
║  工作目录: ~/projects/backend/api_____________________________      ║
║           [Tab: 自动补全] [↑↓: 历史记录]                            ║
║                                                                      ║
║  选择模板:                                                           ║
║    ○ 不使用模板                                                     ║
║    ● API开发模板                                                    ║
║    ○ 前端开发模板                                                   ║
║    ○ 数据分析模板                                                   ║
║    ○ [+] 创建新模板                                                 ║
║                                                                      ║
║  标签: [✓] API开发  [✓] 后端  [ ] 紧急  [ ] 重构                  ║
║                                                                      ║
║  预设任务 (来自模板):                                                ║
║    ✓ 设计 API 接口                                                  ║
║    ✓ 实现数据模型                                                   ║
║    ✓ 编写业务逻辑                                                   ║
║    ✓ 添加单元测试                                                   ║
║    ✓ 编写 API 文档                                                  ║
║    + 添加自定义任务...                                              ║
║                                                                      ║
║  [创建并启动] [取消]                                                 ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### 4.3 性能监控视图
```
╔══════════════════════════════════════════════════════════════════════╗
║                           会话性能监控                                ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  会话: API重构 (abc123)                                             ║
║                                                                      ║
║  CPU 使用率:  ████████░░░░░░░░░░░░  42%  [当前/平均: 42%/35%]      ║
║  内存占用:    ██████░░░░░░░░░░░░░░  312MB / 1024MB                ║
║                                                                      ║
║  运行时间: 2小时 35分钟                                             ║
║  活跃时间: 2小时 10分钟 (84%)                                       ║
║  闲置时间: 25分钟                                                   ║
║                                                                      ║
║  CPU 历史 (最近1小时):                                              ║
║  100% ┤                                                             ║
║   80% ┤                    ╱╲                                       ║
║   60% ┤                   ╱  ╲    ╱╲                               ║
║   40% ┤──────────────────╱────╲──╱──╲─────────                    ║
║   20% ┤                              ╲╱                            ║
║    0% └─────────────────────────────────────────────────────        ║
║       0                   30min                        60min         ║
║                                                                      ║
║  [实时刷新中...] [暂停] [导出数据] [返回]                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

## 5. 安装与配置

### 5.1 系统要求
- macOS 10.15 或更高版本
- iTerm2 3.0 或更高版本
- Python 3.9 或更高版本
- Claude API 访问权限

### 5.2 安装步骤

#### 自动安装（推荐）
```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/ClaudeCode-Cola.git
cd ClaudeCode-Cola

# 2. 运行安装脚本
./install.sh
```

安装脚本会自动完成：
- 创建虚拟环境
- 安装 Python 依赖
- 创建目录结构
- 配置命令别名
- 设置开机自启动（可选）

#### 手动安装
详见完整文档...

### 5.3 首次配置
```bash
# 运行配置向导
cccl --setup
```

配置内容：
1. **Claude API 设置**
   - Base URL
   - API Key
   - Model Name

2. **基础设置**
   - 默认工作目录
   - 刷新间隔
   - 日志保留天数

3. **性能监控**
   - 闲置阈值
   - CPU 告警阈值
   - 监控间隔

4. **通知设置**
   - 通知级别
   - 通知类型开关

## 6. 使用指南

### 6.1 基本命令
```bash
# 启动管理器
cccl

# 后台运行
cccl --daemon

# 查看状态
cccl --status

# 停止服务
cccl --stop

# 备份数据
cccl --backup

# 清理日志
cccl --clean
```

### 6.2 快捷键
- `N` - 新建会话
- `R` - 恢复会话
- `T` - 使用模板
- `S` - 打开设置
- `H` - 显示帮助
- `Q` - 退出程序

### 6.3 与助手对话示例
```
你: 帮我分析一下当前的工作状态
助手: 分析你的3个活跃会话...

你: 关闭所有已完成的会话
助手: 正在关闭2个已完成的会话...

你: 从API模板创建一个用户管理的会话
助手: 正在使用API模板创建新会话...
```

## 7. 技术实现细节

### 7.1 进程监控
```python
# 使用 psutil 监控进程
def monitor_sessions():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'claude' in proc.info['cmdline']:
            # 提取会话信息
            # 监控CPU和内存
            # 更新状态
```

### 7.2 iTerm2 集成
```python
# 使用 AppleScript 控制 iTerm2
def create_iterm_window(session_name, work_dir):
    script = f'''
    tell application "iTerm"
        create window with default profile
        tell current session of current window
            set name to "[CCCL] {session_name}"
            write text "cd {work_dir} && claude code --dangerously-skip-permissions"
        end tell
    end tell
    '''
    subprocess.run(['osascript', '-e', script])
```

### 7.3 通知系统
```python
# 发送系统通知
def send_notification(title, message, subtitle=""):
    script = f'''
    tell application "iTerm"
        display notification "{message}" with title "{title}" subtitle "{subtitle}" sound name "Glass"
    end tell
    '''
    subprocess.run(['osascript', '-e', script])
```

## 8. 安全与隐私

### 8.1 数据安全
- 所有数据存储在本地
- API Key 等敏感信息已加入 .gitignore
- 不会上传任何数据到云端

### 8.2 权限控制
- 仅监控 Claude Code 相关进程
- 不会访问会话内容
- 所有操作都需要用户确认

## 9. 故障排除

### 9.1 常见问题
1. **找不到会话**
   - 检查 iTerm2 窗口标题
   - 运行 `cccl --scan` 重新扫描

2. **通知不工作**
   - 检查系统通知权限
   - 确认 iTerm2 版本

3. **性能数据不准确**
   - 增加监控间隔
   - 检查 ps 命令权限

### 9.2 日志位置
```
~/Code/ClaudeCode-Cola/.claude-code-manager/logs/
├── manager.log      # 主程序日志
├── sessions/        # 会话日志
└── errors.log       # 错误日志
```

## 10. 未来规划

### 第一阶段
- [ ] Web 界面支持
- [ ] 会话组功能
- [ ] 更多模板预设
- [ ] 导出统计报表

### 第二阶段
- [ ] 多设备同步
- [ ] 团队协作功能
- [ ] API 接口
- [ ] 插件系统

### 第三阶段
- [ ] AI 驱动的自动化
- [ ] 跨平台支持
- [ ] 集成更多工具

## 11. 总结

Claude Code Manager (ClaudeCode-Cola) 不仅仅是一个会话管理工具，更是你的智能工作伙伴。通过集成 AI 助手、性能监控、智能通知等功能，让你的开发工作更加高效、愉悦。

就像可口可乐让人精神焕发一样，ClaudeCode-Cola 让你的编程体验充满活力！