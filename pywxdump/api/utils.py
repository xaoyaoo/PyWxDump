# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         utils.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/01/16
# -------------------------------------------------------------------------------
import base64
import json
import logging
import os
import re
import traceback
from .rjson import ReJson
from functools import wraps


def read_session_local_wxid(session_file):
    try:
        with open(session_file, 'r') as f:
            session = json.load(f)
    except FileNotFoundError:
        logging.error(f"Session file not found: {session_file}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file: {e}")
        return None
    rdata = [k for k in session.keys() if k != "test"]
    return rdata


def read_session(session_file, wxid, arg):
    try:
        with open(session_file, 'r') as f:
            session = json.load(f)
    except FileNotFoundError:
        logging.error(f"Session file not found: {session_file}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file: {e}")
        return None
    return session.get(wxid, {}).get(arg, None)


def get_session_wxids(session_file):
    try:
        with open(session_file, 'r') as f:
            session = json.load(f)
    except FileNotFoundError:
        logging.error(f"Session file not found: {session_file}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file: {e}")
        return None
    return list(session.keys())


def save_session(session_file, wxid, arg, value):
    try:
        with open(session_file, 'r') as f:
            session = json.load(f)
    except FileNotFoundError:
        session = {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file: {e}")
        return False

    if wxid not in session:
        session[wxid] = {}
    if not isinstance(session[wxid], dict):
        session[wxid] = {}
    session[wxid][arg] = value
    try:
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=4, ensure_ascii=False)
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
            return ReJson(9999, body=rdata)

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
