# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         t2.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/21
# -------------------------------------------------------------------------------
from pywxdump import get_wechat_db
user_dirs = get_wechat_db(require_list=["MediaMSG", "MicroMsg", "FTSMSG", "MSG", "Sns", "Emotion"])
print(user_dirs)