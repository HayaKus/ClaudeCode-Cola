#!/bin/bash

# Claude Code Manager 卸载脚本

echo "==================================="
echo "Claude Code Manager 卸载程序"
echo "==================================="
echo ""

# 确认卸载
echo "此操作将："
echo "  - 删除命令行工具 (cccl)"
echo "  - 删除 Python 虚拟环境"
echo "  - 删除已安装的包"
echo ""
echo "数据文件将保留在: ~/Code/ClaudeCode-Cola/.claude-code-manager/"
echo ""
read -p "确定要卸载吗？(y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "卸载已取消"
    exit 0
fi

echo ""
echo "开始卸载..."

# 删除命令行快捷方式
if [ -f "/usr/local/bin/cccl" ]; then
    echo "删除命令行工具..."
    sudo rm -f /usr/local/bin/cccl
    echo "✅ 命令行工具已删除"
fi

# 停用虚拟环境（如果激活的话）
if [[ "$VIRTUAL_ENV" != "" ]]; then
    deactivate 2>/dev/null || true
fi

# 删除虚拟环境
if [ -d "venv" ]; then
    echo "删除虚拟环境..."
    rm -rf venv
    echo "✅ 虚拟环境已删除"
fi

# 清理 Python 缓存
echo "清理 Python 缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
echo "✅ 缓存已清理"

echo ""
echo "==================================="
echo "✅ 卸载完成！"
echo "==================================="
echo ""

# 询问是否删除数据文件
echo "是否要删除所有数据文件？"
echo "数据目录: ~/Code/ClaudeCode-Cola/.claude-code-manager/"
echo "⚠️  警告：这将删除所有会话记录、配置和模板！"
echo ""
read -p "删除数据文件？(y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    DATA_DIR="$HOME/Code/ClaudeCode-Cola/.claude-code-manager"
    if [ -d "$DATA_DIR" ]; then
        rm -rf "$DATA_DIR"
        echo "✅ 数据文件已删除"
    fi
else
    echo "数据文件已保留"
fi

echo ""
echo "感谢使用 Claude Code Manager！"
echo "再见！👋"