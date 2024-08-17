# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         utils.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/01/16
# -------------------------------------------------------------------------------
import base64
import json
import os
import random
import re
import string
import traceback
from .rjson import ReJson
from functools import wraps
import logging

server_loger = logging.getLogger("server")
rs_loger = server_loger
ls_loger = server_loger


class ConfData(object):
    _instances = None

    def __new__(cls, *args, **kwargs):
        if cls._instances:
            return cls._instances
        cls._instances = object.__new__(cls)
        return cls._instances

    def __init__(self):
        self._work_path = None
        self.conf_file = None
        self.auto_setting = None

        self.is_init = False

        self.conf = {}

        self.init()

    @property
    def cf(self):
        if not self.is_init:
            self.init()
        return self.conf_file

    @property
    def work_path(self):
        if not self.is_init:
            self.init()
        return self._work_path

    @property
    def at(self):
        if not self.is_init:
            self.init()
        return self.auto_setting

    def init(self):
        self.is_init = False

        work_path = os.getenv("PYWXDUMP_WORK_PATH")
        conf_file = os.getenv("PYWXDUMP_CONF_FILE")
        auto_setting = os.getenv("PYWXDUMP_AUTO_SETTING")

        if work_path is None or conf_file is None or auto_setting is None:
            return False

        self._work_path = work_path
        self.conf_file = conf_file
        self.auto_setting = auto_setting
        self.is_init = True
        
        if not os.path.exists(self.conf_file):
            self.set_conf(self.auto_setting, "last", "")
        self.read_conf()
        return True

    def read_conf(self):
        if not os.path.exists(self.conf_file):
            return False
        try:
            with open(self.conf_file, 'r') as f:
                conf = json.load(f)
                self.conf = conf
                return True
        except FileNotFoundError:
            logging.error(f"Session file not found: {self.conf_file}")
            return False
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON file: {e}")
            return False

    def write_conf(self):
        if not self.is_init:
            self.init()
        try:
            with open(self.conf_file, 'w') as f:
                json.dump(self.conf, f, indent=4, ensure_ascii=False)
                return True
        except Exception as e:
            logging.error(f"Error writing to file: {e}")
            return False

    def set_conf(self, wxid, arg, value):
        if not self.is_init:
            self.init()
        if wxid not in self.conf:
            self.conf[wxid] = {}
        if not isinstance(self.conf[wxid], dict):
            self.conf[wxid] = {}
        self.conf[wxid][arg] = value
        self.write_conf()

    def get_conf(self, wxid, arg):
        if not self.is_init:
            self.init()
        return self.conf.get(wxid, {}).get(arg, None)

    def get_local_wxids(self):
        if not self.is_init:
            self.init()
        return list(self.conf.keys())

    def get_db_config(self):
        if not self.is_init:
            self.init()
        my_wxid = self.get_conf(self.at, "last")
        return self.get_conf(my_wxid, "db_config")


gc: ConfData = ConfData()


def get_conf_local_wxid(conf_file):
    try:
        with open(conf_file, 'r') as f:
            conf = json.load(f)
    except FileNotFoundError:
        logging.error(f"Session file not found: {conf_file}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file: {e}")
        return None
    return list(conf.keys())


def get_conf(conf_file, wxid, arg):
    try:
        with open(conf_file, 'r') as f:
            conf = json.load(f)
    except FileNotFoundError:
        logging.error(f"Session file not found: {conf_file}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file: {e}")
        return None
    return conf.get(wxid, {}).get(arg, None)


def get_conf_wxids(conf_file):
    try:
        with open(conf_file, 'r') as f:
            conf = json.load(f)
    except FileNotFoundError:
        logging.error(f"Session file not found: {conf_file}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file: {e}")
        return None
    return list(conf.keys())


def set_conf(conf_file, wxid, arg, value):
    try:
        with open(conf_file, 'r') as f:
            conf = json.load(f)
    except FileNotFoundError:
        conf = {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file: {e}")
        return False

    if wxid not in conf:
        conf[wxid] = {}
    if not isinstance(conf[wxid], dict):
        conf[wxid] = {}
    conf[wxid][arg] = value
    try:
        with open(conf_file, 'w') as f:
            json.dump(conf, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error writing to file: {e}")
        return False
    return True


def is_port_in_use(_host, _port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((_host, _port))
        except socket.error:
            return True
    return False


def validate_title(title):
    """
    校验文件名是否合法
    """
    rstr = r"[\/\\\:\*\?\"\<\>\|\.]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


def error9999(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback_data = traceback.format_exc()
            rdata = f"{traceback_data}"
            # logging.error(rdata)
            return ReJson(9999, body=f"{str(e)}\n{rdata}", error=str(e))

    return wrapper


def asyncError9999(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            traceback_data = traceback.format_exc()
            rdata = f"{traceback_data}"
            # logging.error(rdata)
            return ReJson(9999, body=f"{str(e)}\n{rdata}", error=str(e))

    return wrapper


def gen_base64(path):
    # 获取文件名后缀
    extension = os.path.splitext(path)[1]
    if extension == '.js':
        start_str = 'data:text/javascript;base64,'
    elif extension == '.css':
        start_str = 'data:text/css;base64,'
    elif extension == '.html':
        start_str = 'data:text/html;base64,'
    elif extension == '.json':
        start_str = 'data:application/json;base64,'
    else:
        start_str = 'data:text/plain;base64,'

    with open(path, 'rb') as file:
        js_code = file.read()

    base64_encoded_js = base64.b64encode(js_code).decode('utf-8')
    return start_str + base64_encoded_js


def random_str(num=16):
    return ''.join(random.sample(string.ascii_letters + string.digits, num))
