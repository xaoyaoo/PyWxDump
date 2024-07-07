# 对象存储文件处理类（示例：假设是 AWS S3）
import os
from typing import IO
from urllib.parse import urlparse

from botocore.exceptions import ClientError
from smart_open import open
import boto3
from botocore.client import Config

class S3Attachment:

    def __init__(self):
        # 腾讯云 COS 配置
        self.cos_endpoint = "https://cos.<your-region>.myqcloud.com"  # 替换 <your-region> 为你的 COS 区域，例如 ap-shanghai
        self.access_key_id = "SecretId"  # 替换为你的腾讯云 SecretId
        self.secret_access_key = "SecretKey"  # 替换为你的腾讯云 SecretKey

        # 创建 S3 客户端
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.cos_endpoint,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=Config(s3={"addressing_style": "virtual", "signature_version": 's3v4'})
        )

    def exists(self, path) -> bool:
        bucket_name, path = self.dealS3Url(path)
        # 检查是否为目录
        if path.endswith('/'):
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
        else:
            # 检查是否为文件
            try:
                self.s3_client.head_object(Bucket=bucket_name, Key=path)
                return True
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    return False
                else:
                    print(f"Error: {e}")
                    return False

    def makedirs(self, path) -> bool:
        if not self.exists(path):
            bucket_name, path = self.dealS3Url(path)
            self.s3_client.put_object(Bucket=bucket_name, Key=f'{path}/')
        return True

    def open(self, path, mode) -> IO:
        self.dealS3Url(path)
        return open(uri=path, mode=mode, transport_params={'client': self.s3_client})

    @classmethod
    def join(cls, __a: str, *paths: str) -> str:
        return os.path.join(__a, *paths)

    @classmethod
    def dirname(cls, path: str) -> str:
        return os.path.dirname(path)

    @classmethod
    def basename(cls, path: str) -> str:
        return os.path.basename(path)

    def dealS3Url(self, path: str) -> object:
        """
        解析 S3 URL 并返回存储桶名称和路径

        参数:
        path (str): S3 URL

        返回:
        tuple: 包含存储桶名称和路径的元组
        """
        parsed_url = urlparse(path)

        # 确保URL是S3 URL
        if parsed_url.scheme != 's3':
            raise ValueError("URL必须是S3 URL，格式为s3://bucket_name/path")

        bucket_name = parsed_url.netloc
        s3_path = parsed_url.path.lstrip('/')

        return bucket_name, s3_path

