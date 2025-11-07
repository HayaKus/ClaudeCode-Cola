# Claude Code Monitor 🔍

一个用于监控Mac上所有Claude Code会话和TodoWrite状态的实时监控工具。

## 功能特性

- 🔍 **全局监控**：自动扫描并监控所有Claude Code会话
- 📝 **TodoWrite追踪**：实时显示每个会话的TodoWrite任务状态
- 🟢 **活跃状态**：识别活跃和非活跃会话
- 📊 **统计面板**：显示会话总数、活跃数、任务进度等
- 🔄 **实时更新**：文件变化时自动更新显示
- 🎨 **美观界面**：使用Rich库构建的终端UI

## 安装和运行

### 首次启动

第一次使用时需要安装依赖：

```bash
# 1. 进入项目目录
cd /Users/haya/Code/ClaudeCode-Cola

# 2. 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip3 install -r requirements.txt

# 4. 运行监控器
python3 claude_monitor.py
```

### 日常启动

#### 方法1：使用启动脚本（推荐）

```bash
cd /Users/haya/Code/ClaudeCode-Cola
./run.sh
```

启动脚本会自动：
- 激活虚拟环境
- 安装/更新依赖
- 启动监控程序

#### 方法2：手动启动

```bash
cd /Users/haya/Code/ClaudeCode-Cola
source venv/bin/activate  # 如果使用虚拟环境
python3 claude_monitor.py
```

### 关闭程序

有以下几种方式关闭监控程序：

1. **正常关闭**（推荐）：按 `Ctrl+C`
   - 程序会优雅地关闭所有监控器和清理资源

2. **强制关闭**：连续按两次 `Ctrl+C`
   - 如果程序没有响应，可以强制退出

3. **通过活动监视器**：
   - 打开Mac的活动监视器
   - 搜索 `python3` 或 `claude_monitor`
   - 选中进程并点击停止按钮

## 界面说明

监控界面分为以下几个部分：

1. **标题栏**：显示程序名称
2. **统计面板**：显示总会话数、活跃会话、TodoWrite项目数、待完成任务数
3. **会话列表**：
   - 🟢 活跃会话（30分钟内有活动）
   - 🔴 非活跃会话
   - 显示项目名、会话ID、持续时间、消息数、TodoWrite进度
4. **TodoWrite汇总**：
   - 任务统计（已完成/进行中/待处理）
   - 最新任务列表

## 监控原理

1. **数据源**：监控 `~/.claude/projects/` 目录下的所有 `.jsonl` 文件
2. **实时监控**：使用 watchdog 监听文件系统变化
3. **进程监控**：使用 psutil 监控 Claude 进程状态
4. **增量读取**：只读取文件新增内容，提高性能

## 快捷键

- `Ctrl+C`：退出程序

## 注意事项

- 首次启动时会扫描所有历史会话，可能需要几秒钟
- 会话文件较多时（1000+）可能会占用一定内存
- 建议在独立终端窗口中运行，以获得最佳显示效果

## 作者

哈雅 (263321)