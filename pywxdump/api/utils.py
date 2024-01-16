# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         utils.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/01/16
# -------------------------------------------------------------------------------
import json


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


if __name__ == '__main__':
    pass
