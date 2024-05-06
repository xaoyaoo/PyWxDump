# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         test_real_time_msg.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/05/06
# -------------------------------------------------------------------------------
from pywxdump import all_merge_real_time_db

key = "jikoagesrgjolaeri456456454523asdf413"
wx_path = "C:/*****/Tencent/WeChat Files/wxid_*****"
merge_path = "C:/merge_all.db"

code, ret = all_merge_real_time_db(key=key, wx_path=wx_path, merge_path=merge_path)
if code:
    print("合并成功: ", ret)
else:
    print(ret)
