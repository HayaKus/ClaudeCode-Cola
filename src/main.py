#!/usr/bin/env python3
"""
ClaudeCode-Cola Mac 应用入口
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.app import ColaApp
from src.utils.logger import setup_logger


def main():
    """应用主入口"""
    # 设置日志
    logger = setup_logger()
    logger.info("🥤 ClaudeCode-Cola 启动中...")

    # 启用高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # 创建 QApplication 实例
    app = QApplication(sys.argv)

    # 设置应用信息
    app.setApplicationName("ClaudeCode-Cola")
    app.setApplicationDisplayName("ClaudeCode-Cola 🥤")
    app.setOrganizationName("Haya")
    app.setOrganizationDomain("com.haya.claudecode-cola")

    # 创建并启动主应用
    cola_app = ColaApp()
    cola_app.show()

    # 进入事件循环
    logger.info("✅ ClaudeCode-Cola 已启动")
    
    try:
        exit_code = app.exec()
    except Exception as e:
        logger.error(f"应用运行出错: {e}")
        exit_code = 1
    
    logger.info("👋 ClaudeCode-Cola 已退出")
    sys.stdout.flush()  # 确保日志输出
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
