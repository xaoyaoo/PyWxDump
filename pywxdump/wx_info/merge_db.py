# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         merge_db.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/12/03
# -------------------------------------------------------------------------------
import logging
import os
import random
import shutil
import sqlite3
import subprocess
import time
from typing import List

def merge_copy_db(db_path, save_path):
    if isinstance(db_path, list) and len(db_path) == 1:
        db_path = db_path[0]
    if not os.path.exists(db_path):
        raise FileNotFoundError("目录不存在")
    shutil.move(db_path, save_path)


# 合并相同名称的数据库 MSG0-MSG9.db
def merge_msg_db(db_path: list, save_path: str, CreateTime: int = 0):  # CreateTime: 从这个时间开始的消息 10位时间戳
    # 判断save_path是否为文件夹
    if os.path.isdir(save_path):
        save_path = os.path.join(save_path, "merge_MSG.db")

    merged_conn = sqlite3.connect(save_path)
    merged_cursor = merged_conn.cursor()

    for db_file in db_path:
        c_tabels = merged_cursor.execute(
            "select tbl_name from sqlite_master where  type='table' and tbl_name!='sqlite_sequence'")
        tabels_all = c_tabels.fetchall()  # 所有表名
        tabels_all = [row[0] for row in tabels_all]

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 创建表
        if len(tabels_all) < 4:
            cursor.execute(
                "select tbl_name,sql from sqlite_master where type='table' and tbl_name!='sqlite_sequence'")
            c_part = cursor.fetchall()

            for tbl_name, sql in c_part:
                if tbl_name in tabels_all:
                    continue
                try:
                    merged_cursor.execute(sql)
                    tabels_all.append(tbl_name)
                except Exception as e:
                    print(f"error: {db_file}\n{tbl_name}\n{sql}\n{e}\n**********")
                    raise e
                merged_conn.commit()

        # 写入数据
        for tbl_name in tabels_all:
            if tbl_name == "MSG":
                MsgSvrIDs = merged_cursor.execute(
                    f"select MsgSvrID from MSG where CreateTime>{CreateTime} and MsgSvrID!=0").fetchall()

                cursor.execute(f"PRAGMA table_info({tbl_name})")
                columns = cursor.fetchall()
                columns = [column[1] for column in columns[1:]]

                ex_sql = f"select {','.join(columns)} from {tbl_name} where CreateTime>{CreateTime} and MsgSvrID not in ({','.join([str(MsgSvrID[0]) for MsgSvrID in MsgSvrIDs])})"
                cursor.execute(ex_sql)

                insert_sql = f"INSERT INTO {tbl_name} ({','.join(columns)}) VALUES ({','.join(['?' for _ in range(len(columns))])})"
                try:
                    merged_cursor.executemany(insert_sql, cursor.fetchall())
                except Exception as e:
                    print(
                        f"error: {db_file}\n{tbl_name}\n{insert_sql}\n{cursor.fetchall()}\n{len(cursor.fetchall())}\n{e}\n**********")
                    raise e
                merged_conn.commit()
            else:
                ex_sql = f"select * from {tbl_name}"
                cursor.execute(ex_sql)

                for r in cursor.fetchall():
                    cursor.execute(f"PRAGMA table_info({tbl_name})")
                    columns = cursor.fetchall()
                    if len(columns) > 1:
                        columns = [column[1] for column in columns[1:]]
                        values = r[1:]
                    else:
                        columns = [columns[0][1]]
                        values = [r[0]]

                        query_1 = "select * from " + tbl_name + " where " + columns[0] + "=?"  # 查询语句 用于判断是否存在
                        c2 = merged_cursor.execute(query_1, values)
                        if len(c2.fetchall()) > 0:  # 已存在
                            continue
                    query = "INSERT INTO " + tbl_name + " (" + ",".join(columns) + ") VALUES (" + ",".join(
                        ["?" for _ in range(len(values))]) + ")"

                    try:
                        merged_cursor.execute(query, values)
                    except Exception as e:
                        print(f"error: {db_file}\n{tbl_name}\n{query}\n{values}\n{len(values)}\n{e}\n**********")
                        raise e
                merged_conn.commit()

        conn.close()
    sql = '''delete from MSG where localId in (SELECT localId from MSG
       where MsgSvrID != 0  and MsgSvrID in (select MsgSvrID  from MSG
                          where MsgSvrID != 0 GROUP BY MsgSvrID  HAVING COUNT(*) > 1)
         and localId not in (select min(localId)  from MSG
                             where MsgSvrID != 0  GROUP BY MsgSvrID HAVING COUNT(*) > 1))'''
    c = merged_cursor.execute(sql)
    merged_conn.commit()
    merged_conn.close()
    return save_path


def merge_media_msg_db(db_path: list, save_path: str):
    # 判断save_path是否为文件夹
    if os.path.isdir(save_path):
        save_path = os.path.join(save_path, "merge_Media.db")
    merged_conn = sqlite3.connect(save_path)
    merged_cursor = merged_conn.cursor()

    for db_file in db_path:

        s = "select tbl_name,sql from sqlite_master where  type='table' and tbl_name!='sqlite_sequence'"
        have_tables = merged_cursor.execute(s).fetchall()
        have_tables = [row[0] for row in have_tables]

        conn_part = sqlite3.connect(db_file)
        cursor = conn_part.cursor()

        if len(have_tables) < 1:
            cursor.execute(s)
            table_part = cursor.fetchall()
            tblname, sql = table_part[0]

            sql = "CREATE TABLE Media(localId INTEGER  PRIMARY KEY AUTOINCREMENT,Key TEXT,Reserved0 INT,Buf BLOB,Reserved1 INT,Reserved2 TEXT)"
            try:
                merged_cursor.execute(sql)
                have_tables.append(tblname)
            except Exception as e:
                print(f"error: {db_file}\n{tblname}\n{sql}\n{e}\n**********")
                raise e
            merged_conn.commit()

        for tblname in have_tables:
            s = "select Reserved0 from " + tblname
            merged_cursor.execute(s)
            r0 = merged_cursor.fetchall()

            ex_sql = f"select `Key`,Reserved0,Buf,Reserved1,Reserved2 from {tblname} where Reserved0 not in ({','.join([str(r[0]) for r in r0])})"
            cursor.execute(ex_sql)
            data = cursor.fetchall()

            insert_sql = f"INSERT INTO {tblname} (Key,Reserved0,Buf,Reserved1,Reserved2) VALUES ({','.join(['?' for _ in range(5)])})"
            try:
                merged_cursor.executemany(insert_sql, data)
            except Exception as e:
                print(f"error: {db_file}\n{tblname}\n{insert_sql}\n{data}\n{len(data)}\n{e}\n**********")
                raise e
            merged_conn.commit()
        conn_part.close()

    merged_conn.close()
    return save_path


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
    except Exception as e:
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
        except Exception as e:
            print(f"**********\nSQL: {sql}\nparams: {params}\n{e}\n**********")
            return None


def merge_db(db_paths, save_path="merge.db", CreateTime: int = 0, endCreateTime: int = 0):
    """
    合并数据库 会忽略主键以及重复的行。
    :param db_paths:
    :param save_path:
    :param CreateTime:
    :return:
    """
    if os.path.isdir(save_path):
        save_path = os.path.join(save_path, f"merge_{int(time.time())}.db")

    if isinstance(db_paths, list):
        # alias, file_path
        databases = {f"MSG{i}": db_path for i, db_path in enumerate(db_paths)}
    elif isinstance(db_paths, str):
        # 判断是否是文件or文件夹
        if os.path.isdir(db_paths):
            db_paths = [os.path.join(db_paths, i) for i in os.listdir(db_paths) if i.endswith(".db")]
            databases = {f"MSG{i}": db_path for i, db_path in enumerate(db_paths)}
        elif os.path.isfile(db_paths):
            databases = {"MSG": db_paths}
        else:
            raise FileNotFoundError("db_paths 不存在")
    else:
        raise TypeError("db_paths 类型错误")

    outdb = sqlite3.connect(save_path)
    out_cursor = outdb.cursor()
    # 将MSG_db_paths中的数据合并到out_db_path中
    for alias in databases:
        db = sqlite3.connect(databases[alias])
        # 获取表名
        sql = f"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        tables = execute_sql(db, sql)
        try:
            for table in tables:
                table = table[0]
                if table == "sqlite_sequence":
                    continue
                # 获取表中的字段名
                sql = f"PRAGMA table_info({table})"
                columns = execute_sql(db, sql)
                if not columns or len(columns) < 1:
                    continue
                col_type = {
                    (i[1] if isinstance(i[1], str) else i[1].decode(), i[2] if isinstance(i[2], str) else i[2].decode())
                    for
                    i in columns}
                columns = [i[1] if isinstance(i[1], str) else i[1].decode() for i in columns]
                if not columns or len(columns) < 1:
                    continue

                # 检测表是否存在
                sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
                out_cursor.execute(sql)
                if len(out_cursor.fetchall()) < 1:
                    # 创建表
                    # 拼接创建表的SQL语句
                    column_definitions = []
                    for column in col_type:
                        column_name = column[0] if isinstance(column[0], str) else column[0].decode()
                        column_type = column[1] if isinstance(column[1], str) else column[1].decode()
                        column_definition = f"{column_name} {column_type}"
                        column_definitions.append(column_definition)
                    sql = f"CREATE TABLE IF NOT EXISTS {table} ({','.join(column_definitions)})"
                    # sql = f"CREATE TABLE IF NOT EXISTS {table} ({','.join(columns)})"
                    out_cursor.execute(sql)

                    # 创建包含 NULL 值比较的 UNIQUE 索引
                    index_name = f"{table}_unique_index"
                    coalesce_columns = ','.join(f"COALESCE({column}, '')" for column in columns)  # 将 NULL 值转换为 ''
                    sql = f"CREATE UNIQUE INDEX IF NOT EXISTS {index_name} ON {table} ({coalesce_columns})"
                    out_cursor.execute(sql)

                # 获取表中的数据
                if "CreateTime" in columns and CreateTime > 0:
                    sql = f"SELECT {','.join([i[0] for i in col_type])} FROM {table} WHERE CreateTime>? ORDER BY CreateTime"
                    src_data = execute_sql(db, sql, (CreateTime,))
                else:
                    sql = f"SELECT {','.join([i[0] for i in col_type])} FROM {table}"
                    src_data = execute_sql(db, sql)
                if not src_data or len(src_data) < 1:
                    continue
                # 插入数据
                sql = f"INSERT OR IGNORE INTO {table} ({','.join([i[0] for i in col_type])}) VALUES ({','.join(['?'] * len(columns))})"
                try:
                    out_cursor.executemany(sql, src_data)
                except Exception as e:
                    logging.error(f"error: {alias}\n{table}\n{sql}\n{src_data}\n{len(src_data)}\n{e}\n**********")
                outdb.commit()
        except Exception as e:
            logging.error(f"fun(merge_db) error: {alias}\n{e}\n**********")
        db.close()
    outdb.close()
    return save_path


def decrypt_merge(wx_path, key, outpath="", CreateTime: int = 0, endCreateTime: int = 0, db_type: List[str] = []) -> (bool, str):
    """
    解密合并数据库 msg.db, microMsg.db, media.db,注意：会删除原数据库
    :param wx_path: 微信路径 eg: C:\*******\WeChat Files\wxid_*********
    :param key: 解密密钥
    :return: (true,解密后的数据库路径) or (false,错误信息)
    """
    from .decryption import batch_decrypt
    from .get_wx_info import get_core_db

    outpath = outpath if outpath else "decrypt_merge_tmp"
    merge_save_path = os.path.join(outpath, "merge_all.db")
    decrypted_path = os.path.join(outpath, "decrypted")

    if not wx_path or not key:
        return False, "参数错误"

    # 分割wx_path的文件名和父目录
    msg_dir = os.path.dirname(wx_path)
    my_wxid = os.path.basename(wx_path)
    db_type_set: set[str] = {"MSG", "MediaMSG", "MicroMsg", "OpenIMContact", "OpenIMMedia", "OpenIMMsg", "Favorite"}
    if len(db_type) == 0:
        db_type = list(db_type_set)
    else:
        for i in db_type:
            if i not in db_type_set:
                return False, f"db_type参数错误, 可用选项 {db_type_set}"
    # 解密
    code, wxdbpaths = get_core_db(wx_path, db_type)
    if not code:
        return False, wxdbpaths
    # 判断out_path是否为空目录
    if os.path.exists(decrypted_path) and os.listdir(decrypted_path):
        for root, dirs, files in os.walk(decrypted_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    if not os.path.exists(decrypted_path):
        os.makedirs(decrypted_path)

    # 调用 decrypt 函数，并传入参数   # 解密
    code, ret = batch_decrypt(key, wxdbpaths, decrypted_path, False)
    if not code:
        return False, ret

    out_dbs = []
    for code1, ret1 in ret:
        if code1:
            out_dbs.append(ret1[1])
    parpare_merge_db_path = []
    for i in out_dbs:
        for j in db_type:
            if j in i:
                parpare_merge_db_path.append(i)
                break
    de_db_type = [f"de_{i}" for i in db_type]
    parpare_merge_db_path = [i for i in out_dbs if any(keyword in i for keyword in de_db_type)]

    merge_save_path = merge_db(parpare_merge_db_path, merge_save_path, CreateTime=CreateTime,
                               endCreateTime=endCreateTime)

    return True, merge_save_path


def merge_real_time_db(key, db_path: str, merge_path: str, CreateTime: int = 0, endCreateTime: int = 9999999999):
    """
    合并实时数据库消息,暂时只支持64位系统
    :param key:  解密密钥
    :param db_path:  数据库路径
    :param merge_path:  合并后的数据库路径
    :param CreateTime:  从这个时间开始的消息 10位时间戳
    :param endCreateTime:  结束时间
    :return:
    """
    try:
        import platform
    except:
        raise ImportError("未找到模块 platform")
    # 判断系统位数是否为64位，如果不是则抛出异常
    if platform.architecture()[0] != '64bit':
        raise Exception("System is not 64-bit.")

    if not os.path.exists(db_path):
        raise FileNotFoundError("数据库不存在")

    if "MSG" not in db_path and "MicroMsg" not in db_path and "MediaMSG" not in db_path:
        raise FileNotFoundError("数据库不是消息数据库")  # MicroMsg实时数据库

    out_path = "tmp_" + ''.join(
        random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6)) + ".db"
    merge_path_base = os.path.dirname(merge_path)  # 合并后的数据库路径
    out_path = os.path.join(merge_path_base, out_path)
    if os.path.exists(out_path):
        os.remove(out_path)

    # 获取当前文件夹路径
    current_path = os.path.dirname(__file__)

    real_time_exe_path = os.path.join(current_path, "tools", "realTime.exe")

    # 调用cmd命令
    cmd = f"{real_time_exe_path} \"{key}\" \"{db_path}\" \"{out_path}\" {CreateTime} {endCreateTime}"
    # os.system(cmd)
    p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         creationflags=subprocess.CREATE_NO_WINDOW)
    p.communicate()

    if not os.path.exists(out_path):
        raise FileNotFoundError("合并失败")

    a = merge_db([out_path], merge_path, CreateTime=CreateTime, endCreateTime=endCreateTime)
    try:
        os.remove(out_path)
    except:
        time.sleep(3)
        os.remove(out_path)

    return True, merge_path


def all_merge_real_time_db(key, wx_path, merge_path):
    """
    合并所有实时数据库
    注：这是全量合并，会有可能产生重复数据，需要自行去重
    :param key:  解密密钥
    :param wx_path:  微信路径
    :param merge_path:  合并后的数据库路径 eg: C:\*******\WeChat Files\wxid_*********\merge.db
    :return:
    """
    if not merge_path or not key or not wx_path or not wx_path:
        return False, "msg_path or media_path or wx_path or key is required"
    try:
        from pywxdump import get_core_db
    except ImportError:
        return False, "未找到模块 pywxdump"

    db_paths = get_core_db(wx_path, ["MediaMSG", "MSG", "MicroMsg"])
    if not db_paths[0]:
        return False, db_paths[1]
    db_paths = db_paths[1]
    for i in db_paths:
        merge_real_time_db(key=key, db_path=i, merge_path=merge_path)
    return True, merge_path
