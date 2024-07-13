# 本地文件处理类
import os
import sys
from typing import IO

from pywxdump.file.Attachment import Attachment


def singleton(cls):
    instances = {}

    def create_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return create_instance


@singleton
class LocalAttachment(Attachment):

    def open(self, path, mode) -> IO:
        """
        打开一个文件并返回文件对象。

        参数:
        path (str): 文件路径。
        mode (str): 打开文件的模式。

        返回:
        IO: 文件对象。
        """
        path = self.dealLocalPath(path)
        return open(path, mode)

    def remove(self, path: str) -> bool:
        """
        删除文件

        参数:
        path (str): 文件路径

        返回:
        bool: 是否删除成功
        """
        path = self.dealLocalPath(path)
        if not self.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        if self.isdir(path):
            raise ValueError(f"Path is not a file: {path}")

        os.remove(path)
        return True

    def exists(self, path) -> bool:
        """
        检查文件或目录是否存在。

        参数:
        path (str): 文件或目录路径。

        返回:
        bool: 如果存在返回True，否则返回False。
        """
        path = self.dealLocalPath(path)
        return os.path.exists(path)

    def makedirs(self, path) -> bool:
        """
        创建目录，包括所有中间目录。

        参数:
        path (str): 目录路径。

        返回:
        bool: 总是返回True。
        """
        path = self.dealLocalPath(path)
        os.makedirs(path)
        return True

    @classmethod
    def join(cls, path: str, *paths: str) -> str:
        """
        连接一个或多个路径组件。

        参数:
        path (str): 第一个路径组件。
        *paths (str): 其他路径组件。

        返回:
        str: 连接后的路径。
        """
        # 使用os.path.join连接路径
        return os.path.join(path, *paths)

    @classmethod
    def dirname(cls, path: str) -> str:
        """
        获取路径的目录名。

        参数:
        path (str): 文件路径。

        返回:
        str: 目录名。
        """
        # 获取路径的目录名
        return os.path.dirname(path)

    @classmethod
    def basename(cls, path: str) -> str:
        """
        获取路径的基本名（文件名）。

        参数:
        path (str): 文件路径。

        返回:
        str: 基本名（文件名）。
        """
        # 获取路径的基本名
        return os.path.basename(path)

    def dealLocalPath(self, path: str) -> str:
        """
        处理本地路径，替换路径中的分隔符，并根据操作系统进行特殊处理。

        参数:
        path (str): 文件路径。

        返回:
        str: 处理后的路径。
        """
        # 获取当前系统的路径分隔符
        # 将path中的 / 替换为当前系统的分隔符
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

    def isdir(self, path: str) -> bool:

        """
        判断是否为目录

        参数:
        path (str): 文件路径

        返回:
        bool: 是否为目录
        """
        # 判断路径是否为目录
        return os.path.isdir(path)

    def getsize(self, path) -> int:
        """
        获取文件大小

        参数:
        path (str): 文件路径

        返回:
        int: 文件大小
        """
        if not self.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        if os.path.isfile(path):
            return os.path.getsize(path)
        else:
            return self._get_dir_size(path)

    def _get_dir_size(self, path):
        """
        计算目录大小

        参数:
        path (str): 目录路径

        返回:
        int: 目录大小
        """
        total_size = 0
        for firePath, surnames, filenames in os.walk(path):
            for f in filenames:
                fp = self.join(firePath, f)
                total_size += os.path.getsize(fp)
        return total_size
