# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         merge_db.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/12/03
# -------------------------------------------------------------------------------
import os
import shutil
import sqlite3


def merge_copy_db(db_path, save_path):
    if isinstance(db_path, list) and len(db_path) == 1:
        db_path = db_path[0]
    if not os.path.exists(db_path):
        raise FileNotFoundError("目录不存在")
    shutil.move(db_path, save_path)


# 合并相同名称的数据库 MSG0-MSG9.db
def merge_msg_db(db_path: list, save_path: str, CreateTime: int = 0):  # CreateTime: 从这个时间开始的消息 10位时间戳

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
