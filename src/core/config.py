"""
配置管理模块
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ClaudeAPIConfig:
    """Claude API 配置"""
    base_url: str = "https://api.anthropic.com"
    api_key: str = ""
    model_name: str = "claude-3-opus-20240229"


@dataclass
class GeneralConfig:
    """常规配置"""
    default_work_dir: str = "~/projects"
    log_retention_days: int = 30
    auto_refresh: bool = True
    refresh_interval: int = 5


@dataclass
class PerformanceConfig:
    """性能监控配置"""
    inactive_threshold_minutes: int = 30
    high_cpu_threshold: float = 80.0
    monitor_interval: int = 10


@dataclass
class NotificationConfig:
    """通知配置"""
    enabled: bool = True
    level: str = "important"  # all, important, none
    todo_complete: bool = True
    session_inactive: bool = True
    session_crashed: bool = True
    high_resource_usage: bool = True


@dataclass
class Config:
    """应用配置"""
    claude_api: ClaudeAPIConfig = field(default_factory=ClaudeAPIConfig)
    general: GeneralConfig = field(default_factory=GeneralConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "claude_api": {
                "base_url": self.claude_api.base_url,
                "api_key": self.claude_api.api_key,
                "model_name": self.claude_api.model_name
            },
            "general": {
                "default_work_dir": self.general.default_work_dir,
                "log_retention_days": self.general.log_retention_days,
                "auto_refresh": self.general.auto_refresh,
                "refresh_interval": self.general.refresh_interval
            },
            "performance": {
                "inactive_threshold_minutes": self.performance.inactive_threshold_minutes,
                "high_cpu_threshold": self.performance.high_cpu_threshold,
                "monitor_interval": self.performance.monitor_interval
            },
            "notifications": {
                "enabled": self.notifications.enabled,
                "level": self.notifications.level,
                "todo_complete": self.notifications.todo_complete,
                "session_inactive": self.notifications.session_inactive,
                "session_crashed": self.notifications.session_crashed,
                "high_resource_usage": self.notifications.high_resource_usage
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """从字典创建"""
        config = cls()

        # Claude API 配置
        if "claude_api" in data:
            api = data["claude_api"]
            config.claude_api = ClaudeAPIConfig(
                base_url=api.get("base_url", config.claude_api.base_url),
                api_key=api.get("api_key", config.claude_api.api_key),
                model_name=api.get("model_name", config.claude_api.model_name)
            )

        # 常规配置
        if "general" in data:
            gen = data["general"]
            config.general = GeneralConfig(
                default_work_dir=gen.get("default_work_dir", config.general.default_work_dir),
                log_retention_days=gen.get("log_retention_days", config.general.log_retention_days),
                auto_refresh=gen.get("auto_refresh", config.general.auto_refresh),
                refresh_interval=gen.get("refresh_interval", config.general.refresh_interval)
            )

        # 性能配置
        if "performance" in data:
            perf = data["performance"]
            config.performance = PerformanceConfig(
                inactive_threshold_minutes=perf.get("inactive_threshold_minutes", config.performance.inactive_threshold_minutes),
                high_cpu_threshold=perf.get("high_cpu_threshold", config.performance.high_cpu_threshold),
                monitor_interval=perf.get("monitor_interval", config.performance.monitor_interval)
            )

        # 通知配置
        if "notifications" in data:
            notif = data["notifications"]
            config.notifications = NotificationConfig(
                enabled=notif.get("enabled", config.notifications.enabled),
                level=notif.get("level", config.notifications.level),
                todo_complete=notif.get("todo_complete", config.notifications.todo_complete),
                session_inactive=notif.get("session_inactive", config.notifications.session_inactive),
                session_crashed=notif.get("session_crashed", config.notifications.session_crashed),
                high_resource_usage=notif.get("high_resource_usage", config.notifications.high_resource_usage)
            )

        return config


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: Optional[Path] = None):
        """初始化配置管理器"""
        if config_path is None:
            self.config_path = Path.home() / "Code" / "ClaudeCode-Cola" / ".claude-code-manager" / "config.json"
        else:
            self.config_path = config_path

        self.config = self.load()

    def load(self) -> Config:
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return Config.from_dict(data)
            except Exception as e:
                print(f"加载配置失败: {e}")
                return Config()
        else:
            # 如果配置文件不存在，创建默认配置
            config = Config()
            self.save(config)
            return config

    def save(self, config: Optional[Config] = None) -> None:
        """保存配置"""
        if config is None:
            config = self.config

        # 确保目录存在
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存配置
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

    def update(self, **kwargs) -> None:
        """更新配置"""
        # 更新 Claude API 配置
        if "claude_api" in kwargs:
            for key, value in kwargs["claude_api"].items():
                setattr(self.config.claude_api, key, value)

        # 更新常规配置
        if "general" in kwargs:
            for key, value in kwargs["general"].items():
                setattr(self.config.general, key, value)

        # 更新性能配置
        if "performance" in kwargs:
            for key, value in kwargs["performance"].items():
                setattr(self.config.performance, key, value)

        # 更新通知配置
        if "notifications" in kwargs:
            for key, value in kwargs["notifications"].items():
                setattr(self.config.notifications, key, value)

        # 保存配置
        self.save()

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """获取配置值"""
        section_obj = getattr(self.config, section, None)
        if section_obj:
            return getattr(section_obj, key, default)
        return default