# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         t2.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/21
# -------------------------------------------------------------------------------
from pywxdump.wx_info import read_info

from pywxdump import WX_OFFS_PATH, WX_OFFS

def test_read_info():
    result = read_info(WX_OFFS, is_logging=True)  # 读取微信信息
    assert result is not None