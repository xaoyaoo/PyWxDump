# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         get_wx_decrypted_db.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/08/25
# -------------------------------------------------------------------------------
import argparse
import os
import re
import shutil
import sqlite3
# import sys
import winreg

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from decrypted.decrypt import decrypt


# 开始获取微信数据库
def get_wechat_db():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat", 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, "FileSavePath")
        winreg.CloseKey(key)
        w_dir = value
    except Exception as e:
        try:
            w_dir = "MyDocument:"
        except Exception as e:
            print("读取注册表错误:", str(e))
            return str(e)

    if w_dir == "MyDocument:":
        profile = os.path.expanduser("~")
        msg_dir = os.path.join(profile, "Documents", "WeChat Files")
    else:
        msg_dir = os.path.join(w_dir, "WeChat Files")
    if not os.path.exists(msg_dir):
        return FileNotFoundError("目录不存在")
    user_dirs = {}  # wx用户目录
    files = os.listdir(msg_dir)
    for file_name in files:
        if file_name == "All Users" or file_name == "Applet" or file_name == "WMPF":
            continue
        user_dirs[file_name] = os.path.join(msg_dir, file_name)

    # 获取数据库路径
    for user, user_dir in user_dirs.items():
        Media_p = []
        Micro_p = []
        FTS_p = []
        Sns_p = []
        Msg = []
        Emotion_p = []
        for root, dirs, files in os.walk(user_dir):
            for file_name in files:
                if re.match(r".*MediaMSG.*\.db$", file_name):
                    src_path = os.path.join(root, file_name)
                    Media_p.append(src_path)
                elif re.match(r".*MicroMsg.*\.db$", file_name):
                    src_path = os.path.join(root, file_name)
                    Micro_p.append(src_path)
                elif re.match(r".*FTSMSG.*\.db$", file_name):
                    src_path = os.path.join(root, file_name)
                    FTS_p.append(src_path)
                elif re.match(r".*MSG.*\.db$", file_name):
                    src_path = os.path.join(root, file_name)
                    Msg.append(src_path)
                elif re.match(r".*Sns.*\.db$", file_name):
                    src_path = os.path.join(root, file_name)
                    Sns_p.append(src_path)
                elif re.match(r".*Emotion.*\.db$", file_name):
                    src_path = os.path.join(root, file_name)
                    Emotion_p.append(src_path)
        Media_p.sort()
        Msg.sort()
        Micro_p.sort()
        # FTS_p.sort()
        user_dirs[user] = {"MicroMsg": Micro_p, "Msg": Msg, "MediaMSG": Media_p, "Sns": Sns_p, "Emotion": Emotion_p}
    return user_dirs


# 解密所有数据库 paths（文件） 到 decrypted_path（目录）
def all_decrypt(keys, paths, decrypted_path):
    decrypted_paths = []

    for key in keys:
        for path in paths:

            name = os.path.basename(path)  # 文件名
            dtp = os.path.join(decrypted_path, name)  # 解密后的路径
            if not decrypt(key, path, dtp):
                break
            decrypted_paths.append(dtp)
        else:  # for循环正常结束，没有break
            break  # 跳出while循环
    else:
        return False  # while循环正常结束，没有break 解密失败
    return decrypted_paths


def merge_copy_msg_db(db_path, save_path):
    if isinstance(db_path, list) and len(db_path) == 1:
        db_path = db_path[0]
    if not os.path.exists(db_path):
        raise FileNotFoundError("目录不存在")
    shutil.move(db_path, save_path)


# 合并相同名称的数据库
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


if __name__ == '__main__':
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--key", help="解密密钥", nargs="+", required=True)

    # 解析命令行参数
    args = parser.parse_args()

    # 检查是否缺少必要参数，并抛出错误
    if not args.key:
        raise ValueError("缺少必要的命令行参数！请提供密钥。")

    # 从命令行参数获取值
    keys = args.key

    decrypted_ROOT = os.path.join(os.getcwd(), "decrypted")

    if keys is None:
        print("keys is None")
        exit(0)
    if isinstance(keys, str):
        keys = [keys]

    user_dirs = get_wechat_db()
    for user, db_path in user_dirs.items():  # 遍历用户
        MicroMsgPaths = db_path["MicroMsg"]
        MsgPaths = db_path["Msg"]
        MediaMSGPaths = db_path["MediaMSG"]
        # FTSMSGPaths = db_path["FTSMSG"]
        SnsPaths = db_path["Sns"]
        EmotionPaths = db_path["Emotion"]

        decrypted_path_tmp = os.path.join(decrypted_ROOT, user, "tmp")  # 解密后的目录
        if not os.path.exists(decrypted_path_tmp):
            os.makedirs(decrypted_path_tmp)

        MicroMsgDecryptPaths = all_decrypt(keys, MicroMsgPaths, decrypted_path_tmp)
        MsgDecryptPaths = all_decrypt(keys, MsgPaths, decrypted_path_tmp)
        MediaMSGDecryptPaths = all_decrypt(keys, MediaMSGPaths, decrypted_path_tmp)
        SnsDecryptPaths = all_decrypt(keys, SnsPaths, decrypted_path_tmp)
        EmotionDecryptPaths = all_decrypt(keys, EmotionPaths, decrypted_path_tmp)

        # 合并数据库
        decrypted_path = os.path.join(decrypted_ROOT, user)  # 解密后的目录

        MicroMsgDbPath = os.path.join(decrypted_path, "MicroMsg.db")
        MsgDbPath = os.path.join(decrypted_path, "MSG_all.db")
        MediaMSGDbPath = os.path.join(decrypted_path, "MediaMSG_all.db")
        SnsDbPath = os.path.join(decrypted_path, "Sns_all.db")
        EmmotionDbPath = os.path.join(decrypted_path, "Emotion_all.db")

        merge_copy_msg_db(MicroMsgDecryptPaths, MicroMsgDbPath)
        merge_msg_db(MsgDecryptPaths, MsgDbPath, 0)
        merge_media_msg_db(MediaMSGDecryptPaths, MediaMSGDbPath)
        merge_copy_msg_db(SnsDecryptPaths, SnsDbPath)
        merge_copy_msg_db(EmotionDecryptPaths, EmmotionDbPath)

        shutil.rmtree(decrypted_path_tmp)  # 删除临时文件
        print(f"解密完成：{user}, {decrypted_path}")
