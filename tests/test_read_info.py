# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         t2.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/21
# -------------------------------------------------------------------------------
from pywxdump.wx_info import read_info

from pywxdump import VERSION_LIST_PATH, VERSION_LIST

def test_read_info():
    result = read_info(VERSION_LIST, is_logging=True)  # 读取微信信息
    assert result is not None