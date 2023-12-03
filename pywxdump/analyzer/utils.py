# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         utils.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/12/03
# -------------------------------------------------------------------------------
import hashlib


def get_md5(data):
    """
    获取数据的 MD5 值
    :param data: 数据（bytes）
    :return:
    """
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()

if __name__ == '__main__':
    pass
