# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         utils.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/12/03
# -------------------------------------------------------------------------------
import hashlib
import os
import re
import sqlite3
import time


def time_int2str(time_int):
    """
    时间戳转换为时间字符串
    :param time_int: 时间戳
    :return: 时间字符串
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_int))


def read_dict_all_values(data):
    """
    读取字典中所有的值（单层）
    :param dict_data: 字典
    :return: 所有值的list
    """
    result = []
    if isinstance(data, list):
        for item in data:
            result.extend(read_dict_all_values(item))
    elif isinstance(data, dict):
        for key, value in data.items():
            result.extend(read_dict_all_values(value))
    else:
        if isinstance(data, bytes):
            tmp = data.decode("utf-8")
        else:
            tmp = str(data) if isinstance(data, int) else data
        result.append(tmp)

    for i in range(len(result)):
        if isinstance(result[i], bytes):
            result[i] = result[i].decode("utf-8")
    return result


def match_BytesExtra(BytesExtra, pattern=r"FileStorage(.*?)'"):
    """
    匹配 BytesExtra
    :param BytesExtra: BytesExtra
    :param pattern: 匹配模式
    :return:
    """
    if not BytesExtra:
        return False
    BytesExtra = read_dict_all_values(BytesExtra)
    BytesExtra = "'" + "'".join(BytesExtra) + "'"
    # print(BytesExtra)

    match = re.search(pattern, BytesExtra)
    if match:
        video_path = match.group(0).replace("'", "")
        return video_path
    else:
        return ""


def get_type_name(type_id: tuple):
    """
    获取消息类型名称
    :param type_id: 消息类型ID 元组 eg: (1, 0)
    :return:
    """
    type_name_dict = {
        (1, 0): "文本",
        (3, 0): "图片",
        (34, 0): "语音",
        (43, 0): "视频",
        (47, 0): "动画表情",

        (37, 0): "添加好友",  # 感谢 https://github.com/zhyc9de
        (42, 0): "推荐公众号",  # 感谢 https://github.com/zhyc9de
        (48, 0): "地图信息",  # 感谢 https://github.com/zhyc9de
        (49, 40): "分享收藏夹",  # 感谢  https://github.com/zhyc9de
        (49, 53): "接龙",  # 感谢  https://github.com/zhyc9de

        (49, 0): "文件",
        (49, 1): "类似文字消息而不一样的消息",
        (49, 5): "卡片式链接",
        (49, 6): "文件",
        (49, 8): "用户上传的GIF表情",
        (49, 19): "合并转发的聊天记录",
        (49, 33): "分享的小程序",
        (49, 36): "分享的小程序",
        (49, 57): "带有引用的文本消息",
        (49, 63): "视频号直播或直播回放等",
        (49, 87): "群公告",
        (49, 88): "视频号直播或直播回放等",
        (49, 2000): "转账消息",
        (49, 2003): "赠送红包封面",

        (50, 0): "语音通话",
        (10000, 0): "系统通知",
        (10000, 4): "拍一拍",
        (10000, 8000): "系统通知"
    }

    if type_id in type_name_dict:
        return type_name_dict[type_id]
    else:
        return "未知"


def get_name_typeid(type_name: str):
    """
    获取消息类型名称
    :param type_id: 消息类型ID 元组 eg: (1, 0)
    :return:
    """
    type_name_dict = {
        (1, 0): "文本",
        (3, 0): "图片",
        (34, 0): "语音",
        (43, 0): "视频",
        (47, 0): "动画表情",

        (37, 0): "添加好友",  # 感谢 https://github.com/zhyc9de
        (42, 0): "推荐公众号",  # 感谢 https://github.com/zhyc9de
        (48, 0): "地图信息",  # 感谢 https://github.com/zhyc9de
        (49, 40): "分享收藏夹",  # 感谢  https://github.com/zhyc9de
        (49, 53): "接龙",  # 感谢  https://github.com/zhyc9de

        (49, 0): "文件",
        (49, 1): "类似文字消息而不一样的消息",
        (49, 5): "卡片式链接",
        (49, 6): "文件",
        (49, 8): "用户上传的GIF表情",
        (49, 19): "合并转发的聊天记录",
        (49, 33): "分享的小程序",
        (49, 36): "分享的小程序",
        (49, 57): "带有引用的文本消息",
        (49, 63): "视频号直播或直播回放等",
        (49, 87): "群公告",
        (49, 88): "视频号直播或直播回放等",
        (49, 2000): "转账消息",
        (49, 2003): "赠送红包封面",

        (50, 0): "语音通话",
        (10000, 0): "系统通知",
        (10000, 4): "拍一拍",
        (10000, 8000): "系统通知"
    }
    type_tup = []
    for k, v in type_name_dict.items():
        if v == type_name:
            type_tup.append(k)
    return type_tup


def get_md5(data):
    """
    获取数据的 MD5 值
    :param data: 数据（bytes）
    :return:
    """
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


import threading


def get_thread_id():
    current_thread = threading.current_thread()
    thread_id = current_thread.ident
    return thread_id


class DBPool:
    __db_pool = {}
    __thread_pool = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(DBPool, cls).__new__(cls)
        return cls._instance

    @classmethod
    def create_connection(cls, db_path):
        if db_path == "DBPOOL_INIT":
            return
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"数据库文件不存在：{db_path}")

        if db_path not in cls.__db_pool:
            cls.__db_pool[db_path] = sqlite3.connect(db_path, check_same_thread=False)
        cls.connection = cls.__db_pool[db_path]

    def __init__(self, db_path):
        if db_path == "DBPOOL_INIT":
            return
        self.db_path = db_path
        if db_path not in self.__db_pool:
            self.create_connection(db_path)
        self.connection = self.__db_pool.get(db_path)
        # 检查数据库是否关闭
        if not self.connection:
            self.create_connection(db_path)
            self.connection = self.__db_pool.get(db_path)

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection = None

    def close_all(self):
        for db_path, connection in self.__db_pool.items():
            connection.close()
        self.__db_pool.clear()


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
    try:
        # connection.text_factory = bytes
        cursor = connection.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e1:
        try:
            connection.text_factory = bytes
            cursor = connection.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            rdata = cursor.fetchall()
            connection.text_factory = str
            return rdata
        except Exception as e2:
            print(f"**********\nSQL: {sql}\nparams: {params}\n{e1}\n{e2}\n**********")
            return None


if __name__ == '__main__':
    pass
