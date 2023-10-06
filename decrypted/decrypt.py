import argparse
import hmac
import hashlib
import os

from Cryptodome.Cipher import AES

SQLITE_FILE_HEADER = "SQLite format 3\x00"  # SQLite文件头

KEY_SIZE = 32
DEFAULT_PAGESIZE = 4096
DEFAULT_ITER = 64000


# 通过密钥解密数据库
def decrypt(key, db_path, out_path):
    if not os.path.exists(db_path):
        print("[-] db_path File not found!")
        return False
    if not os.path.exists(os.path.dirname(out_path)):
        print("[-] out_path File Path not found!")
        return False

    password = bytes.fromhex(key.strip())
    with open(db_path, "rb") as file:
        blist = file.read()

    salt = blist[:16]
    byteKey = hashlib.pbkdf2_hmac("sha1", password, salt, DEFAULT_ITER, KEY_SIZE)
    first = blist[16:DEFAULT_PAGESIZE]

    mac_salt = bytes([(salt[i] ^ 58) for i in range(16)])
    mac_key = hashlib.pbkdf2_hmac("sha1", byteKey, mac_salt, 2, KEY_SIZE)
    hash_mac = hmac.new(mac_key, first[:-32], hashlib.sha1)
    hash_mac.update(b'\x01\x00\x00\x00')

    if hash_mac.digest() == first[-32:-12]:
        print("[+] Decryption Success")
    else:
        print("[-] Password Error")
        return False

    newblist = [blist[i:i + DEFAULT_PAGESIZE] for i in range(DEFAULT_PAGESIZE, len(blist), DEFAULT_PAGESIZE)]

    with open(out_path, "wb") as deFile:
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
    return True


def batch_decrypt(key, db_path, out_path):
    if not os.path.exists(db_path):
        print("[-] db_path File not found!")
        return False
    if not os.path.exists(os.path.dirname(out_path)):
        print("[-] out_path File Path not found!")
        return False

    if os.path.isfile(db_path) and not os.path.isdir(out_path):
        return decrypt(key, db_path, out_path)
    if os.path.isdir(db_path) and not os.path.isfile(out_path):
        for root, dirs, files in os.walk(db_path):
            for file in files:
                decrypt(key, os.path.join(root, file), os.path.join(out_path, "decrypted" + file))
        return True


if __name__ == '__main__':
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", type=str, help="密钥")
    parser.add_argument("--db_path", type=str, help="加密数据库路径")
    parser.add_argument("--out_path", type=str, help="解密后的数据库路径")

    # 解析命令行参数
    args = parser.parse_args()

    # 检查是否缺少必要参数，并抛出错误
    if not args.key or not args.db_path or not args.out_path:
        raise ValueError("缺少必要的命令行参数！请提供密钥、加密数据库路径和解密后的数据库路径。")

    # 从命令行参数获取值
    key = args.key
    db_path = args.db_path
    out_path = args.out_path

    # 调用 decrypt 函数，并传入参数
    result = batch_decrypt(key, db_path, out_path)
    print(f"{result} done!")
