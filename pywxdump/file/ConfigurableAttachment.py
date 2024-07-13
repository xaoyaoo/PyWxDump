from abc import ABC, abstractmethod

from pywxdump.common.config.oss_config import storage_config
from pywxdump.file.Attachment import Attachment


class ConfigurableAttachment(ABC, Attachment):
    @classmethod
    @abstractmethod
    def load_config(cls, config: storage_config) -> Attachment:
        """设置配置"""
        pass
