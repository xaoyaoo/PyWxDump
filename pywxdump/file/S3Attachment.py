# 对象存储文件处理类（示例：假设是 AWS S3）
import os
from typing import IO
from urllib.parse import urlparse, urljoin

from botocore.exceptions import ClientError
from smart_open import open
import boto3
from botocore.client import Config

from pywxdump.common.config.oss_config import storage_config
from pywxdump.file.Attachment import Attachment
from pywxdump.file.ConfigurableAttachment import ConfigurableAttachment


class S3Attachment(ConfigurableAttachment):

    def __init__(self, s3_config: storage_config):
        # S3 配置
        self.s3_config = s3_config
        # 校验配置
        s3_config.validate_config()

        # 创建 S3 客户端
        self.s3_client = boto3.client(
            's3',
            endpoint_url=s3_config.endpoint_url,
            aws_access_key_id=s3_config.access_key,
            aws_secret_access_key=s3_config.secret_key,
            config=Config(s3={"addressing_style": "virtual", "signature_version": 's3v4'})
        )

    @classmethod
    def load_config(cls, config: storage_config) -> Attachment:
        return cls(config)

    def exists(self, s3_url) -> bool:
        """
        检查对象是否存在

        参数:
        s3_url (str): 对象路径

        返回:
        bool: 是否存在
        """
        bucket_name, path = self.dealS3Url(s3_url)
        # 尝试列出该路径下的对象
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=path, MaxKeys=1)
            if 'Contents' in response:
                return True
            else:
                return False
        except ClientError as e:
            print(f"Error: {e}")
            return False

    def makedirs(self, s3_url) -> bool:
        """
        创建目录

        参数:
        s3_url (str): 目录路径

        返回:
        bool: 是否创建成功
        """
        if not self.exists(s3_url):
            bucket_name, path = self.dealS3Url(s3_url)
            self.s3_client.put_object(Bucket=bucket_name, Key=f'{path}/')
        return True

    def open(self, s3_url, mode) -> IO:
        """
        打开文件

        参数:
        s3_url (str): 文件路径
        mode (str): 打开模式

        返回:
        IO: 文件对象
        """
        return open(uri=s3_url, mode=mode, transport_params={'client': self.s3_client})

    def remove(self, s3_url: str) -> bool:
        """
        删除文件

        参数:
        s3_url (str): 文件路径

        返回:
        bool: 是否删除成功
        """

        if not self.exists(s3_url):
            raise FileNotFoundError(f"File not found: {s3_url}")

        if self.isdir(s3_url):
            raise ValueError(f"Path is not a file: {s3_url}")

        bucket_name, path = self.dealS3Url(s3_url)

        self.s3_client.delete_object(Bucket=bucket_name, Key=path)
        return True

    @classmethod
    def join(cls, s3_url: str, *paths: str) -> str:
        """
        连接路径

        参数:
        s3_url (str): 路径
        *paths (str): 路径

        返回:
        str: 连接后的路径
        """
        # 使用os.path.join连接路径
        path = os.path.join(s3_url, *paths)
        # 将所有反斜杠替换为正斜杠
        return path.replace('\\', '/')

    @classmethod
    def dirname(cls, s3_url: str) -> str:
        """
        返回路径的目录部分

        参数:
        s3_url (str): 路径

        返回:
        str: 路径的目录部分
        """
        return os.path.dirname(s3_url)

    @classmethod
    def basename(cls, s3_url: str) -> str:
        """
        返回路径的最后一个元素

        参数:
        s3_url (str): 路径

        返回:
        str: 路径的最后一个元素
        """
        return os.path.basename(s3_url)

    def dealS3Url(self, s3_url: str) -> object:
        """
        解析 S3 URL 并返回存储桶名称和路径

        参数:
        s3_url (str): S3 URL

        返回:
        tuple: 包含存储桶名称和路径的元组
        """
        parsed_url = urlparse(s3_url)

        # 确保URL是S3 URL
        if parsed_url.scheme != 's3':
            raise ValueError("URL必须是S3 URL，格式为s3://bucket_name/path")

        bucket_name = parsed_url.netloc
        s3_path = parsed_url.path.lstrip('/')

        return bucket_name, s3_path

    def isdir(self, s3_url: str) -> bool:

        """
        判断是否为目录

        参数:
        s3_url (str): 文件路径

        返回:
        bool: 是否为目录
        """

        # 确保目录路径以'/'结尾
        if not s3_url.endswith('/'):
            s3_url += '/'

        bucket_name, path = self.dealS3Url(s3_url)
        # 列出以该 key 为前缀的对象
        response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=path, MaxKeys=1)

        if 'Contents' in response:
            # 存在对象，判断是否为目录
            if response['Contents'][0]['Key'] == path or not path.endswith('/'):
                return False
            else:
                return True
        else:
            return False

    def getsize(self, s3_url) -> int:
        """
        获取文件大小

        参数:
        path (str): 文件路径

        返回:
        int: 文件大小
        """
        if not self.exists(s3_url):
            raise FileNotFoundError(f"File not found: {s3_url}")
        if self.isdir(s3_url):
            return self._get_size_of_directory(s3_url)
        else:
            bucket_name, path = self.dealS3Url(s3_url)
            response = self.s3_client.head_object(Bucket=bucket_name, Key=path)
            return response['ContentLength']

    def _get_size_of_directory(self, s3_url):
        """
        获取目录大小

        参数:
        s3_url (str): 目录路径

        返回:
        int: 目录大小
        """
        bucket_name, path = self.dealS3Url(s3_url)
        total_size = 0

        # 确保目录路径以'/'结尾
        if not path.endswith('/'):
            path += '/'

        # 列出指定目录中的对象
        response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=path)
        if 'Contents' in response:
            for obj in response['Contents']:
                total_size += obj['Size']

        return total_size
