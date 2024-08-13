# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         dbbase.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
import importlib
import os
import sqlite3
import time

from .utils import db_loger
from dbutils.pooled_db import PooledDB


# import logging
#
# db_loger = logging.getLogger("db_prepare")


class DatabaseSingletonBase:
    # _singleton_instances = {}  # 使用字典存储不同db_path对应的单例实例
    _class_name = "DatabaseSingletonBase"
    _db_pool = {}  # 使用字典存储不同db_path对应的连接池

    # def __new__(cls, *args, **kwargs):
    #     if cls._class_name not in cls._singleton_instances:
    #         cls._singleton_instances[cls._class_name] = super().__new__(cls)
    #     return cls._singleton_instances[cls._class_name]

    @classmethod
    def connect(cls, db_config):
        """
        连接数据库，如果增加其他数据库连接，则重写该方法
        :param db_config: 数据库配置
        :return: 连接池
        """
        if not db_config:
            raise ValueError("db_config 不能为空")
        db_key = db_config.get("key", "xaoyaoo_741852963")
        db_type = db_config.get("type", "sqlite")
        if db_key in cls._db_pool and cls._db_pool[db_key] is not None:
            return cls._db_pool[db_key]

        if db_type == "sqlite":
            db_path = db_config.get("path", "")
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"文件不存在: {db_path}")
            pool = PooledDB(
                creator=sqlite3,  # 使用 sqlite3 作为连接创建者
                maxconnections=0,  # 连接池最大连接数
                mincached=4,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                maxusage=1,  # 一个链接最多被重复使用的次数，None表示无限制
                blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
                ping=0,  # ping 数据库判断是否服务正常
                database=db_path
            )
        elif db_type == "mysql":
            mysql_config = {
                'user': db_config['user'],
                'host': db_config['host'],
                'password': db_config['password'],
                'database': db_config['database'],
                'port': db_config['port']
            }
            pool = PooledDB(
                creator=importlib.import_module('pymysql'),  # 使用 mysql 作为连接创建者
                ping=1,  # ping 数据库判断是否服务正常
                **mysql_config
            )
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

        db_loger.info(f"{pool} 连接句柄创建 {db_config}")
        cls._db_pool[db_key] = pool
        return pool


class DatabaseBase(DatabaseSingletonBase):
    _class_name = "DatabaseBase"
    existed_tables = []

    def __init__(self, db_config):
        """
        db_config = {
            "key": "test1",
            "type": "sqlite",
            "path": r"C:\***\wxdump_work\merge_all.db"
        }
        """
        self.config = db_config
        self.pool = self.connect(self.config)
        self.__get_existed_tables()

    def __get_existed_tables(self):
        sql = "SELECT tbl_name FROM sqlite_master WHERE type = 'table' and tbl_name!='sqlite_sequence';"
        existing_tables = self.execute(sql)
        self.existed_tables = [row[0].lower() for row in existing_tables]
        return self.existed_tables

    def tables_exist(self, required_tables: str or list):
        """
        判断该类所需要的表是否存在
        Check if all required tables exist in the database.
        Args:
            required_tables (list or str): A list of table names or a single table name string.
        Returns:
            bool: True if all required tables exist, False otherwise.
        """
        if isinstance(required_tables, str):
            required_tables = [required_tables]
        rbool = all(table.lower() in self.existed_tables for table in (required_tables or []))
        if not rbool: db_loger.warning(f"{required_tables=}\n{self.existed_tables=}\n{rbool=}\n")
        return rbool

    def execute(self, sql, params=None):
        """
        执行SQL语句
        :param sql: SQL语句 (str)
        :param params: 参数 (tuple)
        :return: 查询结果 (list)
        """
        connection = self.pool.connection()
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
                db_loger.error(f"{sql=}\n{params=}\n{e1=}\n{e2=}\n", exc_info=True)
                return None
        finally:
            connection.close()

    def close(self):
        self.pool.close()
        db_loger.info(f"关闭数据库 - {self.config}")

    def __del__(self):
        self.close()

# class MsgDb(DatabaseBase):
#
#     def p(self, *args, **kwargs):
#         sel = "select tbl_name from sqlite_master where type='table'"
#         data = self.execute(sel)
#         # print([i[0] for i in data])
#         return data
#
#
# class MsgDb1(DatabaseBase):
#     _class_name = "MsgDb1"
#
#     def p(self, *args, **kwargs):
#         sel = "select tbl_name from sqlite_master where type='table'"
#         data = self.execute(sel)
#         # print([i[0] for i in data])
#         return data
#
#
# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO,
#                         style='{',
#                         datefmt='%Y-%m-%d %H:%M:%S',
#                         format='[{levelname[0]}] {asctime} [{name}:{levelno}] {pathname}:{lineno} {message}'
#                         )
#
#     config1 = {
#         "key": "test1",
#         "type": "sqlite",
#         "path": r"D:\e_all.db"
#     }
#     config2 = {
#         "key": "test2",
#         "type": "sqlite",
#         "path": r"D:\_call.db"
#     }
#
#     t1 = MsgDb(config1)
#     t1.p()
#     t2 = MsgDb(config2)
#     t2.p()
#     t3 = MsgDb1(config1)
#     t3.p()
#     t4 = MsgDb1(config2)
#     t4.p()
#
#     print(t4._db_pool)
#     # 销毁t1
#     del t1
#     # 销毁t2
#     del t2
#     del t3
#
#     # 销毁t4
#     del t4
#     import time
#     time.sleep(1)
#
#     t1 = MsgDb(config1)
#     t1.p()
#     t2 = MsgDb(config2)
#     t2.p()
#
#
#     print(t2._db_pool)
