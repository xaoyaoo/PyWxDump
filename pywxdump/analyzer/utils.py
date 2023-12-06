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


def attach_databases(connection, databases):
    """
    将多个数据库附加到给定的SQLite连接。
    参数：
    -连接：SQLite连接
    -数据库：包含数据库别名和文件路径的词典
    """
    cursor = connection.cursor()
    for alias, file_path in databases.items():
        attach_command = f"ATTACH DATABASE '{file_path}' AS {alias};"
        cursor.execute(attach_command)
    connection.commit()


def detach_databases(connection, aliases):
    """
    从给定的 SQLite 连接中分离多个数据库。

    参数：
        - connection： SQLite连接
        - aliases：要分离的数据库别名列表
    """
    cursor = connection.cursor()
    for alias in aliases:
        detach_command = f"DETACH DATABASE {alias};"
        cursor.execute(detach_command)
    connection.commit()


def execute_sql(connection, sql, params=None):
    """
    执行给定的SQL语句，返回结果。
    参数：
        - connection： SQLite连接
        - sql：要执行的SQL语句
        - params：SQL语句中的参数
    """
    cursor = connection.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    return cursor.fetchall()

if __name__ == '__main__':
    pass
