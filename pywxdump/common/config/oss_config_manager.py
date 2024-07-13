from typing import Type

from pywxdump.common.config.oss_config.storage_config import StorageConfig
from pywxdump.file.ConfigurableAttachment import ConfigurableAttachment


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class OSSConfigManager:
    def __init__(self):
        self._config_instances = {}
        self._attachment_instance = {}

    def load_config(self, config: StorageConfig):
        config.validate_config()
        self._config_instances[config.type()] = config
        # 清除旧的实例
        self._attachment_instance[config.type()] = None

    def get_config(self, config_type: str) -> StorageConfig:
        return self._config_instances.get(config_type)

    def get_attachment(self, config_type: str, instance_class: Type[ConfigurableAttachment]):
        if config_type not in self._config_instances:
            raise ValueError(f"Config not found: {config_type}")
        if not self._attachment_instance[config_type]:
            config = self._config_instances[config_type]
            self._attachment_instance[config_type] = instance_class.load_config(config)
        return self._attachment_instance[config_type]
