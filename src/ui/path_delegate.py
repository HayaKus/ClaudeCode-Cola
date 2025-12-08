"""
路径显示委托 - 用于在表格中优雅地显示长路径
"""
from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from PyQt6.QtCore import Qt, QModelIndex, QRect
from PyQt6.QtGui import QPainter


class PathItemDelegate(QStyledItemDelegate):
    """
    自定义委托用于显示路径
    当路径过长时,省略前面的部分而不是后面的部分
    """

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        """
        自定义绘制方法

        Args:
            painter: QPainter对象
            option: 样式选项
            index: 模型索引
        """
        # 获取原始文本
        text = index.data(Qt.ItemDataRole.DisplayRole)

        if not text:
            super().paint(painter, option, index)
            return

        # 设置绘制选项
        painter.save()

        # 如果选中,绘制选中背景
        from PyQt6.QtWidgets import QStyle
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(option.palette.text().color())

        # 设置字体
        painter.setFont(option.font)

        # 计算文本矩形
        text_rect = option.rect.adjusted(5, 0, -5, 0)  # 左右各留5px边距

        # 获取字体度量
        font_metrics = painter.fontMetrics()

        # 如果文本太长,从前面省略
        elided_text = font_metrics.elidedText(
            text,
            Qt.TextElideMode.ElideLeft,  # 关键: 从左边(前面)省略
            text_rect.width()
        )

        # 绘制文本
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            elided_text
        )

        painter.restore()
