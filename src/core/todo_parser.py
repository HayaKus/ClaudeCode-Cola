"""
Todo 解析策略
"""
import json
from pathlib import Path
from typing import List

from src.data.models import TodoItem, TodoStatus
from src.utils.logger import logger


class TodoParser:
    """Todo 解析器"""

    @staticmethod
    def parse_claude_todos(jsonl_path: Path) -> List[TodoItem]:
        """
        解析 Claude Code 的 todos（从 jsonl 文件中的 TodoWrite 工具调用）

        实现逻辑：
        1. 逐行读取 jsonl 文件
        2. 查找 message.content 中 type="tool_use" 且 name="TodoWrite" 的记录
        3. 从 input.todos 中提取 todo 列表
        4. 每次找到新的 TodoWrite 都会覆盖之前的（保留最新）
        """
        todos = []
        try:
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())

                        if 'message' in data and 'content' in data['message']:
                            for item in data['message']['content']:
                                if isinstance(item, dict) and \
                                   item.get('type') == 'tool_use' and \
                                   item.get('name') == 'TodoWrite':

                                    if 'input' in item and 'todos' in item['input']:
                                        todos_list = item['input']['todos']
                                        if isinstance(todos_list, list):
                                            todos = []  # 清空，使用最新的
                                            for todo_item in todos_list:
                                                try:
                                                    todo = TodoItem(
                                                        content=todo_item.get('content', ''),
                                                        status=TodoStatus(todo_item.get('status', 'pending')),
                                                        active_form=todo_item.get('activeForm', ''),
                                                    )
                                                    todos.append(todo)
                                                except Exception as e:
                                                    logger.debug(f"解析 Claude Todo 项失败: {e}")
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"读取 Claude Code todos 失败 {jsonl_path}: {e}")

        return todos

    @staticmethod
    def parse_qoder_todos(session_id: str) -> List[TodoItem]:
        """
        解析 Qoder 的 todos（从独立的 json 文件）

        实现逻辑：
        1. 构造 todos 文件路径：~/.qoder/todos/<session_id>.json
        2. 如果文件不存在，返回空列表
        3. 读取 JSON 数组并转换为 TodoItem 列表
        """
        todos = []
        todos_file = Path.home() / '.qoder' / 'todos' / f'{session_id}.json'

        logger.info(f"📝 开始解析 Qoder todos: {session_id}")
        logger.info(f"📂 Todos 文件路径: {todos_file}")
        logger.info(f"📄 文件是否存在: {todos_file.exists()}")

        if not todos_file.exists():
            logger.info(f"⚠️ Qoder todos 文件不存在: {todos_file}")
            return todos

        try:
            with open(todos_file, 'r', encoding='utf-8') as f:
                todos_data = json.load(f)
                logger.info(f"✅ 成功读取 todos 文件，包含 {len(todos_data) if isinstance(todos_data, list) else 0} 个任务")

                if isinstance(todos_data, list):
                    for item in todos_data:
                        try:
                            todo = TodoItem(
                                content=item.get('content', ''),
                                status=TodoStatus(item.get('status', 'pending')),
                                active_form=item.get('activeForm', ''),
                            )
                            todos.append(todo)
                            logger.info(f"  ✓ 解析任务: {todo.status_icon} {todo.content}")
                        except Exception as e:
                            logger.error(f"  ✗ 解析 Qoder Todo 项失败: {e}")

                logger.info(f"🎉 Qoder todos 解析完成，共 {len(todos)} 个任务")
        except Exception as e:
            logger.error(f"❌ 读取 Qoder todos 文件失败 {todos_file}: {e}")

        return todos
