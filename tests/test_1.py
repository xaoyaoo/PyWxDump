# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         test1.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/15
# -------------------------------------------------------------------------------
import pywxdump
from pywxdump import VERSION_LIST_PATH, VERSION_LIST
from pywxdump.bias_addr import BiasAddr
from pywxdump.wx_info import read_info

# bias = BiasAddr("12345678901", "test", "test", "test", "test").run()
wx_info = read_info(VERSION_LIST)
print(wx_info)
