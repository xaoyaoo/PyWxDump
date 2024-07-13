import os
from datetime import datetime
from typing import AnyStr, Callable, Union, IO
from flask import send_file, Response

from pywxdump.common.config.oss_config.s3_config import S3Config
from pywxdump.common.config.oss_config_manager import OSSConfigManager
from pywxdump.file.Attachment import Attachment
from pywxdump.file.LocalAttachment import LocalAttachment
from pywxdump.file.S3Attachment import S3Attachment


def determine_strategy(file_path: str) -> Attachment:
    """
    根据文件路径确定使用的附件策略（本地或S3）。

    参数:
    file_path (str): 文件路径。

    返回:
    Attachment: 返回对应的附件策略类实例。
    """
    if file_path.startswith(f"s3://"):
        return OSSConfigManager().get_attachment("s3", S3Attachment)
    else:
        return LocalAttachment()


def exists(path: str) -> bool:
    """
    检查文件或目录是否存在。

    参数:
    path (str): 文件或目录路径。

    返回:
    bool: 如果存在返回True，否则返回False。
    """
    return determine_strategy(path).exists(path)


def open_file(path: str, mode: str) -> IO:
    """
    打开一个文件并返回文件对象。

    参数:
    path (str): 文件路径。
    mode (str): 打开文件的模式。

    返回:
    IO: 文件对象。
    """
    return determine_strategy(path).open(path, mode)


def makedirs(path: str) -> bool:
    """
    创建目录，包括所有中间目录。

    参数:
    path (str): 目录路径。

    返回:
    bool: 总是返回True。
    """
    return determine_strategy(path).makedirs(path)


def join(path: str, *paths: str) -> str:
    """
    连接一个或多个路径组件。

    参数:
    path (str): 第一个路径组件。
    *paths (str): 其他路径组件。

    返回:
    str: 连接后的路径。
    """
    return determine_strategy(path).join(path, *paths)


def dirname(path: str) -> str:
    """
    获取路径的目录名。

    参数:
    path (str): 文件路径。

    返回:
    str: 目录名。
    """
    return determine_strategy(path).dirname(path)


def basename(path: str) -> str:
    """
    获取路径的基本名（文件名）。

    参数:
    path (str): 文件路径。

    返回:
    str: 基本名（文件名）。
    """
    return determine_strategy(path).basename(path)


def send_attachment(
        path_or_file: Union[os.PathLike[AnyStr], str],
        mimetype: Union[str, None] = None,
        as_attachment: bool = False,
        download_name: Union[str, None] = None,
        conditional: bool = True,
        etag: Union[bool, str] = True,
        last_modified: Union[datetime, int, float, None] = None,
        max_age: Union[None, int, Callable[[Union[str, None]], Union[int, None]]] = None,
) -> Response:
    """
    发送附件文件。

    参数:
    path_or_file (Union[os.PathLike[AnyStr], str]): 文件路径或文件对象。
    mimetype (Union[str, None]): 文件的MIME类型。
    as_attachment (bool): 是否作为附件下载。
    download_name (Union[str, None]): 下载时的文件名。
    conditional (bool): 是否使用条件请求。
    etag (Union[bool, str]): ETag值。
    last_modified (Union[datetime, int, float, None]): 最后修改时间。
    max_age (Union[None, int, Callable[[Union[str, None]], Union[int, None]]]): 缓存最大时间。

    返回:
    Response: Flask的响应对象。
    """
    file_io = open_file(path_or_file, "rb")

    # 如果没有提供 download_name 或 mimetype，则从 path_or_file 中获取文件名和 MIME 类型
    if download_name is None:
        download_name = basename(path_or_file)
    if mimetype is None:
        mimetype = 'application/octet-stream'

    return send_file(file_io, mimetype, as_attachment, download_name, conditional, etag, last_modified, max_age)


def download_file(db_path, local_path):
    """
    从db_path下载文件到local_path。

    参数:
    db_path (str): 数据库文件路径。
    local_path (str): 本地文件路径。

    返回:
    str: 本地文件路径。
    """
    with open(local_path, 'wb') as f:
        with open_file(db_path, 'rb') as r:
            f.write(r.read())
    return local_path


def isLocalPath(path: str) -> bool:
    """
    判断路径是否为本地路径。

    参数:
    path (str): 文件或目录路径。

    返回:
    bool: 如果是本地路径返回True，否则返回False。
    """
    strategy = determine_strategy(path)
    return isinstance(strategy, type(LocalAttachment()))


def getsize(path: str):
    """
    获取文件大小

    参数:
    path (str): 文件路径

    返回:
    int: 文件大小
    """
    return determine_strategy(path).getsize(path)

