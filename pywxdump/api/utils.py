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

rs_loger = logging.getLogger("rs_api")
ls_loger = logging.getLogger("ls_api")


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
