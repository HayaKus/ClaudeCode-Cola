#!/bin/bash

# Claude Code Manager 安装脚本

echo "==================================="
echo "Claude Code Manager (ClaudeCode-Cola) 安装程序"
echo "==================================="
echo ""

# 检查是否在 macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 此工具仅支持 macOS"
    exit 1
fi

# 检查 Python 版本
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) != "$REQUIRED_VERSION" ]]; then
    echo "❌ Python 版本过低。需要 Python 3.8+，当前版本：$PYTHON_VERSION"
    exit 1
fi
echo "✅ Python 版本检查通过：$PYTHON_VERSION"

# 检查 iTerm2
if ! osascript -e 'application "iTerm2" is running' &> /dev/null; then
    echo "⚠️  iTerm2 未运行。请确保已安装 iTerm2"
fi

# 检查 Claude CLI
if ! command -v claude &> /dev/null; then
    echo "⚠️  Claude CLI 未安装。请先安装 Claude CLI"
    echo "   访问: https://claude.ai/cli"
fi

# 创建数据目录
DATA_DIR="$HOME/Code/ClaudeCode-Cola/.claude-code-manager"
echo ""
echo "创建数据目录: $DATA_DIR"
mkdir -p "$DATA_DIR"

# 创建虚拟环境
echo ""
echo "创建 Python 虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
echo ""
echo "升级 pip..."
pip install --upgrade pip

# 安装依赖
echo ""
echo "安装依赖包..."
pip install -r requirements.txt

# 安装包
echo ""
echo "安装 Claude Code Manager..."
pip install -e .

# 创建符号链接
echo ""
echo "创建命令行快捷方式..."

# 获取安装路径
INSTALL_PATH="$(pwd)/venv/bin/cccl"

# 创建 /usr/local/bin 目录（如果不存在）
sudo mkdir -p /usr/local/bin

# 创建包装脚本
WRAPPER_SCRIPT="/usr/local/bin/cccl"
sudo tee "$WRAPPER_SCRIPT" > /dev/null << EOF
#!/bin/bash
# Claude Code Manager wrapper script
source "$(pwd)/venv/bin/activate"
exec "$(pwd)/venv/bin/cccl" "\$@"
EOF

# 设置可执行权限
sudo chmod +x "$WRAPPER_SCRIPT"

# 创建初始配置文件
if [ ! -f "$DATA_DIR/config.json" ]; then
    echo ""
    echo "创建默认配置文件..."
    cat > "$DATA_DIR/config.json" << 'EOF'
{
  "general": {
    "default_work_dir": "~/projects",
    "auto_refresh": true,
    "refresh_interval": 5
  },
  "claude_api": {
    "api_key": "",
    "base_url": "https://api.anthropic.com",
    "model_name": "claude-3-sonnet-20240229"
  },
  "performance": {
    "high_cpu_threshold": 80.0,
    "inactive_threshold_minutes": 30,
    "enable_monitoring": true
  },
  "notifications": {
    "enabled": true,
    "level": "all",
    "todo_complete": true,
    "session_inactive": true,
    "session_crashed": true,
    "high_resource_usage": true
  }
}
EOF
    echo "✅ 配置文件已创建: $DATA_DIR/config.json"
fi

echo ""
echo "==================================="
echo "✅ 安装完成！"
echo "==================================="
echo ""
echo "使用方法："
echo "  cccl          - 启动 Claude Code Manager"
echo "  cccl new      - 快速创建新会话"
echo "  cccl list     - 列出所有会话"
echo "  cccl config   - 编辑配置"
echo "  cccl doctor   - 检查环境"
echo "  cccl --help   - 查看帮助"
echo ""
echo "配置 Claude API："
echo "  编辑 $DATA_DIR/config.json"
echo "  添加你的 API Key 以启用 AI 助手功能"
echo ""
echo "享受你的编程之旅！🚀"