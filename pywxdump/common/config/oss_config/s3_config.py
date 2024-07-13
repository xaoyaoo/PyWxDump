from pywxdump.common.config.oss_config.storage_config import StorageConfig, TYPE_KEY, DescriptionBuilder
from pywxdump.common.config.oss_config.storage_config_factory import StorageConfigFactory

S3 = "s3"
ENDPOINT_URL = "endpoint_url"
SECRET_KEY = "secret_key"
ACCESS_KEY = "access_key"


@StorageConfigFactory.register(S3)
class S3Config(StorageConfig):

    def __init__(self, access_key, secret_key, endpoint_url):
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint_url = endpoint_url

    @classmethod
    def type(cls) -> str:
        return S3

    @classmethod
    def describe(cls):
        builder = DescriptionBuilder()
        builder.add_description(ENDPOINT_URL, "https://cos.<your-regin>.myqcloud.com", ENDPOINT_URL)
        builder.add_description(ACCESS_KEY, "腾讯云的SecretId", ACCESS_KEY)
        builder.add_description(SECRET_KEY, "腾讯云的SecretKey", SECRET_KEY)
        return builder.build()

    def get_config(self):
        return {
            TYPE_KEY: S3,
            ACCESS_KEY: self.access_key,
            SECRET_KEY: self.secret_key,
            ENDPOINT_URL: self.endpoint_url
        }

    def validate_config(self):
        if not self.access_key or not self.secret_key or not self.endpoint_url:
            raise ValueError("S3 configuration is not valid")

    @classmethod
    def value_of(cls, config: dict):
        access_key = config.get(ACCESS_KEY)
        secret_key = config.get(SECRET_KEY)
        endpoint_url = config.get(ENDPOINT_URL)
        s3_config = cls(access_key, secret_key, endpoint_url)
        s3_config.validate_config()
        return s3_config

    @classmethod
    def isSupported(cls, path: str) -> bool:
        if not path:
            return False
        if path.startswith(f"{S3}://"):
            return True


