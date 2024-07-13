from abc import ABC, abstractmethod



TYPE_KEY = "oss_type_key"


class StorageConfig(ABC):

    @classmethod
    @abstractmethod
    def type(cls):
        """返回实现类的类型"""
        pass

    @classmethod
    @abstractmethod
    def describe(cls):
        """返回对象存储的描述"""
        pass

    @abstractmethod
    def get_config(self):
        """返回存储配置的字典"""
        pass

    @abstractmethod
    def validate_config(self):
        """验证配置是否合法"""
        pass

    @classmethod
    @abstractmethod
    def value_of(cls, config: dict):
        pass

    @classmethod
    @abstractmethod
    def isSupported(cls, path: str) -> bool:
        pass


class DescriptionBuilder:
    LABEL = "label"
    PLACEHOLDER = "placeholder"
    KEY = "key"

    def __init__(self):
        self.description = []

    def add_description(self, label, placeholder, key):
        self.description.append({
            self.LABEL: label,
            self.PLACEHOLDER: placeholder,
            self.KEY: key
        })
        return self

    def build(self):
        return self.description
