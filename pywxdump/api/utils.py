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
import traceback
from .rjson import ReJson
from functools import wraps


def read_session(session_file, arg):
    with open(session_file, 'r') as f:
        session = json.load(f)
    return session.get(arg, "")


def save_session(session_file, arg, value):
    try:
        with open(session_file, 'r') as f:
            session = json.load(f)
    except:
        session = {}
    session[arg] = value
    with open(session_file, 'w') as f:
        json.dump(session, f, indent=4)
    return True


def error9999(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback_data = traceback.format_exc()
            rdata = f"{traceback_data}"
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