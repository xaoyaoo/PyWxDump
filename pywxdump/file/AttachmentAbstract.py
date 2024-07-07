from typing import Protocol, IO


# 基类
class Attachment(Protocol):

    def exists(self, path) -> bool:
        pass

    def makedirs(self, path) -> bool:
        pass

    def open(self, path, param) -> IO:
        pass

    @classmethod
    def join(cls, __a: str, *paths: str) -> str:
        pass

    @classmethod
    def dirname(cls, path: str) -> str:
        pass

    @classmethod
    def basename(cls, path: str) -> str:
        pass
