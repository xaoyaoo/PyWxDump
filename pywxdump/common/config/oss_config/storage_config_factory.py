import json
from abc import ABC

from pywxdump.common.config.oss_config.storage_config import TYPE_KEY, StorageConfig


class StorageConfigFactory(ABC):
    registry = {}

    @classmethod
    def register(cls, type_name):
        def inner_wrapper(subclass):
            cls.registry[type_name] = subclass
            return subclass

        return inner_wrapper

    @staticmethod
    def create(json_str) -> StorageConfig:
        config_dict = json.loads(json_str)
        config_type = config_dict.get(TYPE_KEY)
        subclass = StorageConfigFactory.registry.get(config_type)
        if subclass is None:
            raise ValueError(f'Unknown config type: {config_type}')
        return subclass.value_of(config_dict)
