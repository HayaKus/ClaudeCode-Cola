"""
路径解码工具

用于将 Claude Code 和 Qoder CLI 的编码目录名还原为真实路径
"""
from pathlib import Path
from typing import Optional, List
from src.utils.logger import logger


def decode_encoded_dirname(encoded_dirname: str) -> str:
    """
    将编码的目录名还原为真实路径

    Claude Code 和 Qoder CLI 使用 - 作为路径分隔符来创建扁平化的目录结构
    例如: -Users-haya-Code-my-project

    本方法通过检查文件系统实际存在的路径来正确还原:
    - 如果是 /Users/haya/Code/my-project (存在) -> 返回这个
    - 而不是 /Users/haya/Code/my/project (不存在)

    Args:
        encoded_dirname: 编码的目录名,如 "-Users-haya-Code-my-project"

    Returns:
        还原后的真实路径,如 "/Users/haya/Code/my-project"

    算法说明:
        使用回溯法尝试所有可能的分割组合,找到第一个在文件系统中实际存在的完整路径
    """
    # 移除前导的 -
    cleaned = encoded_dirname.lstrip('-')
    if not cleaned:
        return "/"

    # 分割成部分
    parts = cleaned.split('-')

    def backtrack(index: int, current_parts: List[str]) -> Optional[str]:
        """
        使用回溯法尝试所有可能的分割组合
        返回第一个在文件系统中完全存在的路径

        Args:
            index: 当前处理到parts的哪个位置
            current_parts: 已经构建好的路径组件列表

        Returns:
            如果找到存在的路径则返回路径字符串,否则返回None
        """
        if index >= len(parts):
            # 所有parts都处理完了,检查这个路径是否存在
            path_str = '/' + '/'.join(current_parts)
            if Path(path_str).exists():
                return path_str
            return None

        # 选择1: 将当前part作为一个新的路径组件(用/分隔)
        new_parts = current_parts + [parts[index]]
        result = backtrack(index + 1, new_parts)
        if result:
            return result

        # 选择2: 将当前part与上一个组件合并(用-连接)
        if current_parts:  # 确保不是第一个part
            merged_parts = current_parts[:-1] + [current_parts[-1] + '-' + parts[index]]
            result = backtrack(index + 1, merged_parts)
            if result:
                return result

        return None

    result = backtrack(0, [])

    # 如果找不到存在的路径,回退到简单替换
    if result is None:
        result = '/' + cleaned.replace('-', '/')
        logger.warning(
            f"⚠️ 无法通过文件系统验证还原路径,使用简单替换: {encoded_dirname} -> {result}"
        )

    return result
