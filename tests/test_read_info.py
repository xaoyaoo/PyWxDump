# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         t2.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/21
# -------------------------------------------------------------------------------
from pywxdump import get_wx_info, WX_OFFS


def test_read_info():
    result = get_wx_info(WX_OFFS, is_logging=True)  # 读取微信信息
    assert result is not None
