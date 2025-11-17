"""
配置管理模块
"""
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

from src.utils.logger import logger


@dataclass
class Config:
    """应用配置"""

    # 显示设置
    show_window_on_start: bool = True
    theme: str = "auto"  # auto, light, dark

    # 刷新设置
    auto_refresh: bool = True
    refresh_interval: int = 5  # 秒

    # 监控设置
    projects_dir: str = str(Path.home() / ".claude" / "projects")

    # 通知设置
    enable_notifications: bool = True
    notify_on_error: bool = True
    notify_on_inactive: bool = False

    # 窗口设置
    window_width: int = 1000
    window_height: int = 600
    window_x: Optional[int] = None
    window_y: Optional[int] = None

    def __post_init__(self):
        """初始化后加载配置"""
        self.config_file = Path.home() / ".claudecode-cola" / "config.json"
        self.load()

    def load(self):
        """从文件加载配置"""
        if not self.config_file.exists():
            logger.info("配置文件不存在,使用默认配置")
            self.save()
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 更新配置
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            logger.info("配置加载成功")
        except Exception as e:
            logger.error(f"加载配置失败: {e}")

    def save(self):
        """保存配置到文件"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self), f, indent=2, ensure_ascii=False)

            logger.info("配置保存成功")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")

    def get_projects_dir(self) -> Path:
        """获取项目目录路径"""
        return Path(self.projects_dir)

    def set_projects_dir(self, path: str):
        """设置项目目录路径"""
        self.projects_dir = path
        self.save()
