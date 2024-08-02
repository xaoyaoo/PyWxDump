# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         test1.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/15
# -------------------------------------------------------------------------------
import pywxdump
from pywxdump import WX_OFFS_PATH, WX_OFFS
from pywxdump import BiasAddr
from pywxdump.wx_info import read_info

mobile = '13800138000'
name = '张三'
account = 'xxxxxx'
key = None  # "xxxxxx"
db_path = None  # "xxxxxx"
vlp = None  # WX_OFFS_PATH
# 调用 run 函数，并传入参数
rdata = BiasAddr(account, mobile, name, key, db_path).run(True, vlp)

