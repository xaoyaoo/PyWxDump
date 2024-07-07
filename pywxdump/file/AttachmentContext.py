import os
from datetime import datetime
from typing import AnyStr, BinaryIO, Callable, Union, IO
from flask import send_file, Response

from pywxdump.file.AttachmentAbstract import Attachment
from pywxdump.file.LocalAttachment import LocalAttachment
from pywxdump.file.S3Attachment import S3Attachment


def determine_strategy(file_path: str) -> Attachment:
    if file_path.startswith("s3://"):
        return S3Attachment()
    else:
        return LocalAttachment()


def exists(path: str) -> bool:
    return determine_strategy(path).exists(path)


def open_file(path: str, mode: str) -> IO:
    return determine_strategy(path).open(path, mode)


def makedirs(path: str) -> bool:
    return determine_strategy(path).makedirs(path)


def join(__a: str, *paths: str) -> str:
    return determine_strategy(__a).join(__a, *paths)


def dirname(path: str) -> str:
    return determine_strategy(path).dirname(path)


def basename(path: str) -> str:
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
    file_io = open_file(path_or_file, "rb")

    # 如果没有提供 download_name 或 mimetype，则从 path_or_file 中获取文件名和 MIME 类型
    if download_name is None:
        download_name = basename(path_or_file)
    if mimetype is None:
        mimetype = 'application/octet-stream'

    return send_file(file_io, mimetype, as_attachment, download_name, conditional, etag, last_modified, max_age)


def download_file(db_path, local_path):
    with open(local_path, 'wb') as f:
        with open_file(db_path, 'rb') as r:
            f.write(r.read())
    return local_path


def isLocalPath(path: str) -> bool:
    return isinstance(determine_strategy(path), LocalAttachment)

