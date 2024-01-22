# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         utils.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/01/16
# -------------------------------------------------------------------------------
import json
import logging
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
