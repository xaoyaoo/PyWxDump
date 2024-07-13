from typing import Protocol, IO


# 基类
class Attachment(Protocol):
    """
    附件处理协议类，定义了附件处理的基本接口。
    """

    def exists(self, path: str) -> bool:
        """
        检查文件或目录是否存在。

        参数:
        path (str): 文件或目录路径。

        返回:
        bool: 如果存在返回True，否则返回False。
        """
        pass

    def makedirs(self, path: str) -> bool:
        """
        创建目录，包括所有中间目录。

        参数:
        path (str): 目录路径。

        返回:
        bool: 总是返回True。
        """
        pass

    def open(self, path: str, mode: str) -> IO:
        """
        打开一个文件并返回文件对象。

        参数:
        path (str): 文件路径。
        mode (str): 打开文件的模式。

        返回:
        IO: 文件对象。
        """
        pass

    def remove(self, path: str) -> bool:
        """
        删除文件

        参数:
        path (str): 文件路径

        返回:
        bool: 是否删除成功
        """
        pass

    def isdir(self, path: str) -> bool:

        """
        判断是否为目录

        参数:
        s3_url (str): 文件路径

        返回:
        bool: 是否为目录
        """
        pass
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
        pass

    @classmethod
    def dirname(cls, path: str) -> str:
        """
        获取路径的目录名。

        参数:
        path (str): 文件路径。

        返回:
        str: 目录名。
        """
        pass

    @classmethod
    def basename(cls, path: str) -> str:
        """
        获取路径的基本名（文件名）。

        参数:
        path (str): 文件路径。

        返回:
        str: 基本名（文件名）。
        """
        pass

    def getsize(self, path) -> int:
        """
        获取文件大小

        参数:
        path (str): 文件路径

        返回:
        int: 文件大小
        """
        pass


