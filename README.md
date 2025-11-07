# ClaudeCode-Cola 🥤

一个优雅的 Claude Code 会话管理器，专为 macOS + iTerm2 设计。

## 项目简介

ClaudeCode-Cola（简称 CCCL）是一个集中式的 Claude Code 会话管理工具，解决了多个终端窗口关闭后无法追踪会话的问题。它提供了一个友好的界面来管理、监控和恢复你的 Claude Code 会话。

## 主要特性

- 📊 **会话管理** - 创建、查看、恢复和关闭 Claude Code 会话
- 🎯 **模板系统** - 使用预定义模板快速创建特定类型的会话
- 📱 **iTerm2 集成** - 自动管理 iTerm2 窗口标题，格式：`[CCCL] <session-name> - <session-id>`
- 🤖 **AI 助手** - 内置 Claude AI 助手，提供智能建议和帮助
- 📈 **性能监控** - 实时监控会话的 CPU 和内存使用情况
- 🔔 **通知系统** - 会话状态变化时的系统通知
- 💾 **简单存储** - 使用 JSON 文件存储，避免数据库依赖

## 安装要求

- macOS 系统
- Python 3.8+
- iTerm2（可选，但推荐）
- Claude API Key

## 快速安装

```bash
# 克隆项目
git clone <repository-url>
cd ClaudeCode-Cola

# 运行安装脚本
./install.sh

# 配置 API Key
# 编辑 ~/Code/ClaudeCode-Cola/.claude-code-manager/config.json
# 添加你的 Claude API Key
```

## 使用方法

```bash
# 启动管理器
cccl

# 或者使用详细命令
claude-code-manager
```

## 界面功能

管理器提供以下功能：

1. **新建会话** - 创建新的 Claude Code 会话
2. **查看会话** - 查看所有活跃和已关闭的会话
3. **恢复会话** - 恢复已关闭的会话
4. **关闭会话** - 安全关闭运行中的会话
5. **性能监控** - 查看会话资源使用情况
6. **模板管理** - 管理会话模板
7. **AI 助手** - 与 Claude AI 对话获取帮助

## 开发指南

```bash
# 设置开发环境
./dev_setup.sh
source venv/bin/activate

# 运行测试
python test_run.py

# 运行单元测试
pytest tests/
```

## 项目结构

```
ClaudeCode-Cola/
├── src/
│   ├── core/           # 核心功能模块
│   ├── ui/             # 用户界面
│   └── cli.py          # 命令行入口
├── tests/              # 测试文件
├── install.sh          # 安装脚本
├── uninstall.sh        # 卸载脚本
└── config.example.json # 配置模板
```

## 配置说明

配置文件位于 `~/Code/ClaudeCode-Cola/.claude-code-manager/config.json`，主要配置项：

- `claude_api_key` - Claude API Key
- `default_work_dir` - 默认工作目录
- `auto_save_interval` - 自动保存间隔（秒）
- `monitoring_enabled` - 是否启用性能监控
- `notification_enabled` - 是否启用系统通知

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**ClaudeCode-Cola** - 让你的 Claude Code 体验充满活力！ 🎉