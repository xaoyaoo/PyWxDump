# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         dbbase.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
import os
import sqlite3
import logging


class DatabaseBase:
    _singleton_instances = {}  # 使用字典存储不同db_path对应的单例实例
    _connection_pool = {}  # 使用字典存储不同db_path对应的连接池
    _class_name = "DatabaseBase"

    def __new__(cls, db_path):
        if cls._class_name not in cls._singleton_instances:
            cls._singleton_instances[cls._class_name] = super().__new__(cls)
        return cls._singleton_instances[cls._class_name]

    def __init__(self, db_path):
        self._db_path = db_path
        self._db_connection = self._connect_to_database(db_path)

    @classmethod
    def _connect_to_database(cls, db_path):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"文件不存在: {db_path}")
        if db_path in cls._connection_pool and cls._connection_pool[db_path] is not None:
            return cls._connection_pool[db_path]
        connection = sqlite3.connect(db_path, check_same_thread=False)
        logging.info(f"{connection} 连接句柄创建 {db_path}")
        return connection

    def execute_sql(self, sql, params=None):
        """
        执行SQL语句
        :param sql: SQL语句 (str)
        :param params: 参数 (tuple)
        :return: 查询结果 (list)
        """
        # 检测数据库连接是否关闭
        if not self._db_connection:
            logging.warning(f"重新连接数据库 - {self._db_path}")
            self._connect_to_database(self._db_path)
        connection = self._db_connection
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
                logging.error(f"**********\nSQL: {sql}\nparams: {params}\n{e1}\n{e2}\n**********")
                return None

    def close_connection(self):
        if self._db_connection:
            self._db_connection.close()
            logging.info(f"关闭数据库 - {self._db_path}")
            self._db_connection = None

    def close_all_connection(self):
        for db_path in self._connection_pool:
            if self._connection_pool[db_path]:
                self._connection_pool[db_path].close()
                logging.info(f"关闭数据库 - {db_path}")
                self._connection_pool[db_path] = None

    def show__singleton_instances(self):
        print(self._singleton_instances)

    def __del__(self):
        self.close_connection()
        # del self._singleton_instances[self._db_path]


if __name__ == '__main__':
    a = DatabaseBase("test.db")
    b = DatabaseBase("test1.db")

    d1 = a.execute_sql("select * from sqlite_master;")
    d2 = b.execute_sql("select * from sqlite_master;")
    print([i[1] for i in d1])
    print([i[1] for i in d2])

    a.close_connection()
    b.close_connection()
