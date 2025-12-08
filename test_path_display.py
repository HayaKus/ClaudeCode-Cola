#!/usr/bin/env python3
"""
测试路径显示效果
"""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

def test_text_elide():
    """测试Qt的文本省略功能"""
    app = QApplication([])

    from PyQt6.QtGui import QFontMetrics, QFont

    # 创建字体度量对象
    font = QFont()
    font_metrics = QFontMetrics(font)

    # 测试路径
    test_paths = [
        "/Users/haya/Code/ClaudeCode-Cola",
        "/Users/haya/Code/very-long-project-name-that-needs-truncation",
        "/Users/haya/Documents/Projects/MyVeryLongProjectNameThatWillBeTruncated",
    ]

    # 可用宽度(像素)
    available_width = 200

    print("测试路径省略效果:")
    print("=" * 80)
    print(f"可用宽度: {available_width}px\n")

    for path in test_paths:
        # 从右边省略(默认)
        elided_right = font_metrics.elidedText(path, Qt.TextElideMode.ElideRight, available_width)

        # 从左边省略(我们想要的)
        elided_left = font_metrics.elidedText(path, Qt.TextElideMode.ElideLeft, available_width)

        print(f"原始路径: {path}")
        print(f"从右省略: {elided_right}")
        print(f"从左省略: {elided_left}")
        print()

if __name__ == '__main__':
    test_text_elide()
