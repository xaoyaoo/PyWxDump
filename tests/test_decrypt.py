# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         test_decrypt.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/11/15
# -------------------------------------------------------------------------------
from pywxdump import batch_decrypt

key = "xxxxxx"  # 解密密钥
db_path = "xxxxxx"  # 数据库路径（文件or文件list）
out_path = "xxxxxx"  # 输出路径（目录）

result = batch_decrypt(key, db_path, out_path, True)
