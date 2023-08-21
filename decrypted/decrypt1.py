import glob
import os
import hmac
import hashlib
import re
import shutil
import sqlite3
import subprocess
import winreg

from Cryptodome.Cipher import AES

SQLITE_FILE_HEADER = "SQLite format 3\x00"
IV_SIZE = 16
HMAC_SHA1_SIZE = 20
KEY_SIZE = 32
DEFAULT_PAGESIZE = 4096
DEFAULT_ITER = 64000


# 通过密钥解密数据库
def decrypt(key, filePath, decryptedPath):
    password = bytes.fromhex(key.replace(" ", ""))
    with open(filePath, "rb") as file:
        blist = file.read()

    salt = blist[:16]
    byteKey = hashlib.pbkdf2_hmac("sha1", password, salt, DEFAULT_ITER, KEY_SIZE)
    first = blist[16:DEFAULT_PAGESIZE]

    mac_salt = bytes([(salt[i] ^ 58) for i in range(16)])
    mac_key = hashlib.pbkdf2_hmac("sha1", byteKey, mac_salt, 2, KEY_SIZE)
    hash_mac = hmac.new(mac_key, first[:-32], hashlib.sha1)
    hash_mac.update(b'\x01\x00\x00\x00')

    if hash_mac.digest() == first[-32:-12]:
        print("Decryption Success")
    else:
        print("Password Error")

    newblist = [blist[i:i + DEFAULT_PAGESIZE] for i in range(DEFAULT_PAGESIZE, len(blist), DEFAULT_PAGESIZE)]

    with open(decryptedPath, "wb") as deFile:
        deFile.write(SQLITE_FILE_HEADER.encode())
        t = AES.new(byteKey, AES.MODE_CBC, first[-48:-32])
        decrypted = t.decrypt(first[:-48])
        deFile.write(decrypted)
        deFile.write(first[-48:])

        for i in newblist:
            t = AES.new(byteKey, AES.MODE_CBC, i[-48:-32])
            decrypted = t.decrypt(i[:-48])
            deFile.write(decrypted)
            deFile.write(i[-48:])


# 通过外部程序获取微信数据库的key
def get_wx_key():
    """
    执行 GoWxDump.exe -wxinfo 获取微信数据库的key
    :return:
    """
    # 获取当前文件路径的上一级目录
    current_path = os.path.dirname(os.path.abspath(__file__))
    current_path = os.path.abspath(os.path.join(current_path, "../.."))
    # 获取GoWxDump.exe的路径
    gowxdump_path = os.path.join(current_path, "Release", "GoWxDump.exe")
    # 判断GoWxDump.exe是否存在
    if not os.path.exists(gowxdump_path):
        print("GoWxDump.exe not found")
        return
    command = gowxdump_path + " -wxinfo"
    output = subprocess.check_output(command, shell=True, encoding='latin-1')

    wx_key = output.split("WeChat Key:")[-1].strip()
    return wx_key


# 获取微信数据根目录
def get_wechat_dir():
    """
    读取注册表获取微信消息目录
    :return:
    """
    try:
        # 打开注册表的微信路径：HKEY_CURRENT_USER\Software\Tencent\WeChat\FileSavePath
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat", 0, winreg.KEY_READ)
        # 获取key的值
        value, _ = winreg.QueryValueEx(key, "FileSavePath")
        # 关闭注册表项
        winreg.CloseKey(key)
        w_dir = value
    except Exception as e:
        print("读取注册表错误:", str(e))
        return str(e)

    # 如果 w_dir 为 "MyDocument:"
    if w_dir == "MyDocument:":
        # 获取 %USERPROFILE%/Documents 目录
        profile = os.path.expanduser("~")
        # 获取微信消息目录
        msg_dir = os.path.join(profile, "Documents", "WeChat Files")
    else:
        # 获取微信消息目录
        msg_dir = os.path.join(w_dir, "WeChat Files")
    # 判断目录是否存在
    if not os.path.exists(msg_dir):
        raise FileNotFoundError("目录不存在")
    return msg_dir


# 获取微信消息目录下的所有用户目录
def get_wechat_user_dir(wechat_root):
    """
    // 获取微信消息目录下的所有用户目录，排除All Users目录和Applet目录，返回一个map，key用户id，value用户目录
    :param wechat_root:  微信消息目录
    :return:
    """
    user_dirs = {}
    # 获取微信消息目录下的所有用户目录
    files = os.listdir(wechat_root)
    for file_name in files:
        # 排除All Users目录和Applet目录
        if file_name == "All Users" or file_name == "Applet" or file_name == "WMPF":
            continue
        user_dirs[file_name] = os.path.join(wechat_root, file_name)
    return user_dirs


# copy msg.db到tmp目录,并创建decrypted目录
def copy_msg_db(data_dir):
    # 判断目录是否存在
    if not os.path.exists(data_dir):
        raise FileNotFoundError("目录不存在")

    # 判断运行目录是否存在tmp目录，如果不存在则创建
    tmp_dir = os.path.join(os.getcwd(), "tmp")
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    # 正则匹配，将所有MSG数字.db文件拷贝到tmp目录，不扫描子目录
    for root, dirs, files in os.walk(data_dir):
        for file_name in files:
            if re.match(r".*MSG.*\.db", file_name):
                src_path = os.path.join(root, file_name)
                dst_path = os.path.join(tmp_dir, file_name)
                shutil.copyfile(src_path, dst_path)

        if "MicroMsg.db" in files:
            src_path = os.path.join(root, "MicroMsg.db")
            dst_path = os.path.join(tmp_dir, "MicroMsg.db")
            shutil.copyfile(src_path, dst_path)

    # 如果不存在decrypted目录则创建
    decrypted_dir = os.path.join(os.getcwd(), "")
    if not os.path.exists(decrypted_dir):
        os.mkdir(decrypted_dir)
    return tmp_dir, decrypted_dir


# 合并相同名称的数据库
def merge_db(db_path):
    dbs_paths = {}
    for root, dirs, files in os.walk(db_path):
        for file_name in files:
            if "db-shm" in file_name or "db-wal" in file_name:
                continue
            if "FTSMSG" in file_name:
                src_path = os.path.join(root, file_name)
                dbs_paths["FTSMSG_all.db"] = dbs_paths.get("FTSMSG_all.db", [])
                dbs_paths["FTSMSG_all.db"].append(src_path)
            elif "MediaMSG" in file_name:
                src_path = os.path.join(root, file_name)
                dbs_paths["MediaMSG_all.db"] = dbs_paths.get("MediaMSG_all.db", [])
                dbs_paths["MediaMSG_all.db"].append(src_path)
            elif "MSG" in file_name:
                src_path = os.path.join(root, file_name)
                dbs_paths["MSG_all.db"] = dbs_paths.get("MSG_all.db", [])
                dbs_paths["MSG_all.db"].append(src_path)

    for db_name, db_files in dbs_paths.items():
        if db_name != "MSG_all.db":
            continue

        save_path = os.path.join(db_path, db_name)
        merged_conn = sqlite3.connect(save_path)
        merged_cursor = merged_conn.cursor()

        for db_file in db_files:
            c0 = merged_cursor.execute("select tbl_name from sqlite_master where type='table'")
            r0 = c0.fetchall()
            r0 = [row[0] for row in r0]

            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            c = cursor.execute("select tbl_name,sql from sqlite_master where type='table'")
            tbls = []
            for row in c:
                if row[0] == "sqlite_sequence":
                    continue
                if "mmTokenizer" in row[1]:
                    continue
                tbls.append(row[0])
                if row[0] in r0:
                    continue
                try:
                    merged_cursor.execute(row[1])
                except Exception as e:
                    print(e)
                    print(db_file)
                    print(row[1])
                    print(r0)
                    raise e
                merged_conn.commit()
            for row in tbls:
                c1 = cursor.execute("select * from " + row)
                for r in c1:
                    columns = conn.execute("PRAGMA table_info(" + row + ")").fetchall()
                    if len(columns) > 1:
                        columns = [column[1] for column in columns[1:]]
                        values = r[1:]
                        # query = "INSERT INTO " + row + " (" + ",".join(columns) + ") VALUES (" + ",".join(
                        #     ["?" for _ in range(len(values))]) + ")"
                    else:
                        columns = [columns[0][1]]
                        values = [r[0]]
                        query_1 = "select * from " + row + " where " + columns[0] + "=?"
                        c2 = merged_cursor.execute(query_1, values)
                        if len(c2.fetchall()) > 0:
                            continue
                    query = "INSERT INTO " + row + " (" + ",".join(columns) + ") VALUES (" + ",".join(
                        ["?" for _ in range(len(values))]) + ")"

                    try:
                        merged_cursor.execute(query, values)
                    except Exception as e:
                        print()
                        print("error")
                        print(e)
                        print(db_file)
                        print(query, values)
                        print(len(values))
                        raise e
                merged_conn.commit()

            conn.close()
            print(db_file)

        merged_conn.close()
        # merge_databases(save_path, db_file)


def merge_databases(db1, db2):
    con3 = sqlite3.connect(db1)

    con3.execute("ATTACH DATABASE '" + db2 + "' as dba")

    con3.execute("BEGIN")
    for row in con3.execute("SELECT * FROM dba.sqlite_master WHERE type='table'"):
        # 此处的ignore就是为了忽略重复ID导致的异常
        combine = "INSERT OR IGNORE INTO " + row[1] + " SELECT * FROM dba." + row[1]
        print(combine)
        con3.execute(combine)
    con3.commit()
    con3.execute("detach database dba")


if __name__ == '__main__':
    # 获取微信数据库的key
    wx_key = get_wx_key()

    # 获取微信消息目录
    wechat_msg_dir = get_wechat_dir()
    user_msg_dirs = get_wechat_user_dir(wechat_msg_dir)
    if len(user_msg_dirs) == 1:
        data_dir = list(user_msg_dirs.values())[0]
    else:
        for i, user_dir in enumerate(user_msg_dirs):
            print(i, user_dir)
        index = int(input("请选择要导出的用户："))
        data_dir = list(user_msg_dirs.values())[index]

    print("复制微信的msg数据文件...")
    # 复制微信的msg数据文件
    tmp_dir, decrypted_dir = copy_msg_db(os.path.join(data_dir, "Msg"))

    print("解密数据库...")
    # 解密数据库
    for file_name in os.listdir(tmp_dir):
        if re.match(r".*\.db$", file_name):
            src_path = os.path.join(tmp_dir, file_name)
            dst_path = os.path.join(decrypted_dir, file_name)
            decrypt(wx_key, src_path, dst_path)

    # 删除临时目录
    shutil.rmtree(tmp_dir)

    # decrypted_dir = os.path.join(os.getcwd(), "decrypted")
    print("合并数据库...")
    # 合并数据库
    merge_db(decrypted_dir)
