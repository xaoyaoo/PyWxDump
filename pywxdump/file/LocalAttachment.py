# 本地文件处理类
import os
import sys
from typing import IO


class LocalAttachment:

    def open(self, path, mode) -> IO:
        path = self.dealLocalPath(path)
        return open(path, mode)

    def exists(self, path) -> bool:
        path = self.dealLocalPath(path)
        return os.path.exists(path)

    def makedirs(self, path) -> bool:
        path = self.dealLocalPath(path)
        os.makedirs(path)
        return True

    @classmethod
    def join(cls, __a: str, *paths: str) -> str:
        return os.path.join(__a, *paths)

    @classmethod
    def dirname(cls, path: str) -> str:
        return os.path.dirname(path)

    @classmethod
    def basename(cls, path: str) -> str:
        return os.path.basename(path)

    def dealLocalPath(self, path: str) -> str:
        # 获取当前系统的地址分隔符
        # 将path中的 /替换为当前系统的分隔符
        path = path.replace('/', os.sep)
        if sys.platform == "win32":
            # 如果是windows系统，且路径长度超过260个字符
            if len(path) >= 260:
                # 添加前缀
                return '\\\\?\\' + path
            else:
                return path
        else:
            return path
