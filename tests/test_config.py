"""测试配置管理"""
import pytest
import json
import tempfile
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.config import ConfigManager, ClaudeAPIConfig, GeneralConfig


class TestConfigManager:
    """测试配置管理器"""

    def test_default_config(self):
        """测试默认配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))

            # 测试默认值
            assert config_manager.config.general.default_work_dir == "~/projects"
            assert config_manager.config.general.auto_refresh == True
            assert config_manager.config.general.refresh_interval == 5

            assert config_manager.config.performance.high_cpu_threshold == 80.0
            assert config_manager.config.performance.inactive_threshold_minutes == 30

    def test_load_save_config(self):
        """测试配置的加载和保存"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"

            # 创建测试配置
            test_config = {
                "general": {
                    "default_work_dir": "~/test",
                    "auto_refresh": False,
                    "refresh_interval": 10
                },
                "claude_api": {
                    "api_key": "test_key",
                    "base_url": "https://test.com",
                    "model_name": "test-model"
                }
            }

            # 写入配置文件
            with open(config_path, "w") as f:
                json.dump(test_config, f)

            # 加载配置
            config_manager = ConfigManager(Path(tmpdir))

            # 验证加载的值
            assert config_manager.config.general.default_work_dir == "~/test"
            assert config_manager.config.general.auto_refresh == False
            assert config_manager.config.claude_api.api_key == "test_key"

    def test_update_config(self):
        """测试更新配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))

            # 更新配置
            config_manager.config.general.default_work_dir = "~/updated"
            config_manager.config.claude_api.api_key = "new_key"

            # 保存配置
            config_manager.save_config()

            # 重新加载验证
            new_manager = ConfigManager(Path(tmpdir))
            assert new_manager.config.general.default_work_dir == "~/updated"
            assert new_manager.config.claude_api.api_key == "new_key"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])