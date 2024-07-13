import json
from dataclasses import dataclass

from pywxdump.common.config.oss_config.storage_config import StorageConfig


@dataclass
class ServerConfig:
    """
    :param merge_path:  合并后的数据库路径  默认""
    :param wx_path:  微信文件夹的路径（用于显示图片） 默认""
    :param key:  密钥 默认""
    :param my_wxid:  微信账号(本人微信id) 默认""
    :param port:  端口号 默认5000
    :param online:  是否在线查看(局域网查看) 默认 False
    :param debug:  是否开启debug模式 默认 False
    :param is_open_browser:  是否自动打开浏览器 默认 True
    :param oss_config: 对象存储配置 默认 None
    """
    merge_path: str = ""
    wx_path: str = ""
    key: str = ""
    my_wxid: str = ""
    port: int = 5000
    online: bool = False
    debug: bool = False
    is_open_browser: bool = True
    oss_config: dict = None

    @classmethod
    def builder(cls):
        return ServerConfig.Builder()

    class Builder:
        def __init__(self):
            self._merge_path = ""
            self._wx_path = ""
            self._key = ""
            self._my_wxid = ""
            self._port = 5000
            self._online = False
            self._debug = False
            self._is_open_browser = True
            self._oss_config = None

        def merge_path(self, merge_path: str):
            self._merge_path = merge_path
            return self

        def wx_path(self, wx_path: str):
            self._wx_path = wx_path
            return self

        def key(self, key: str):
            self._key = key
            return self

        def my_wxid(self, my_wxid: str):
            self._my_wxid = my_wxid
            return self

        def port(self, port: int):
            self._port = port
            return self

        def online(self, online: bool):
            self._online = online
            return self

        def debug(self, debug: bool):
            self._debug = debug
            return self

        def is_open_browser(self, is_open_browser: bool):
            self._is_open_browser = is_open_browser
            return self

        def oss_config(self, oss_config: StorageConfig):
            oss_config.validate_config()
            self._oss_config = oss_config.get_config()
            return self

        def build(self):
            return ServerConfig(
                merge_path=self._merge_path,
                wx_path=self._wx_path,
                key=self._key,
                my_wxid=self._my_wxid,
                port=self._port,
                online=self._online,
                debug=self._debug,
                is_open_browser=self._is_open_browser,
                oss_config=self._oss_config
            )

    def oss_config_to_json(self) -> str:
        return json.dumps(self.oss_config) if self.oss_config else None
