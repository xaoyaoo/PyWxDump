# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         getwxinfo.py
# Description:
# Author:       xaoyaoo
# Date:         2023/08/21
# 注：该部分注释为最初学习使用，仅作参考
# 微信数据库采用的加密算法是256位的AES-CBC。数据库的默认的页大小是4096字节即4KB，其中每一个页都是被单独加解密的。
# 加密文件的每一个页都有一个随机的初始化向量，它被保存在每一页的末尾。
# 加密文件的每一页都存有着消息认证码，算法使用的是HMAC-SHA1（安卓数据库使用的是SHA512）。它也被保存在每一页的末尾。
# 每一个数据库文件的开头16字节都保存了一段唯一且随机的盐值，作为HMAC的验证和数据的解密。
# 为了保证数据部分长度是16字节即AES块大小的整倍数，每一页的末尾将填充一段空字节，使得保留字段的长度为48字节。
# 综上，加密文件结构为第一页4KB数据前16字节为盐值，紧接着4032字节数据，再加上16字节IV和20字节HMAC以及12字节空字节；而后的页均是4048字节长度的加密数据段和48字节的保留段。
# -------------------------------------------------------------------------------
import hmac
import hashlib
import os
from typing import Union, List
from Cryptodome.Cipher import AES
# from Crypto.Cipher import AES # 如果上面的导入失败，可以尝试使用这个

from .utils import wx_core_error, wx_core_loger

SQLITE_FILE_HEADER = "SQLite format 3\x00"  # SQLite文件头

KEY_SIZE = 32
DEFAULT_PAGESIZE = 4096


# 通过密钥解密数据库
@wx_core_error
def decrypt(key: str, db_path: str, out_path: str):
    """
    通过密钥解密数据库
    :param key: 密钥 64位16进制字符串
    :param db_path:  待解密的数据库路径(必须是文件)
    :param out_path:  解密后的数据库输出路径(必须是文件)
    :return:
    """
    if not os.path.exists(db_path) or not os.path.isfile(db_path):
        return False, f"[-] db_path:'{db_path}' File not found!"
    if not os.path.exists(os.path.dirname(out_path)):
        return False, f"[-] out_path:'{out_path}' File not found!"

    if len(key) != 64:
        return False, f"[-] key:'{key}' Len Error!"

    password = bytes.fromhex(key.strip())

    try:
        with open(db_path, "rb") as file:
            blist = file.read()
    except Exception as e:
        return False, f"[-] db_path:'{db_path}' {e}!"

    salt = blist[:16]
    first = blist[16:4096]
    if len(salt) != 16:
        return False, f"[-] db_path:'{db_path}' File Error!"
    mac_salt = bytes([(salt[i] ^ 58) for i in range(16)])
    byteHmac = hashlib.pbkdf2_hmac("sha1", password, salt, 64000, KEY_SIZE)
    mac_key = hashlib.pbkdf2_hmac("sha1", byteHmac, mac_salt, 2, KEY_SIZE)
    hash_mac = hmac.new(mac_key, blist[16:4064], hashlib.sha1)
    hash_mac.update(b'\x01\x00\x00\x00')

    if hash_mac.digest() != first[-32:-12]:
        return False, f"[-] Key Error! (key:'{key}'; db_path:'{db_path}'; out_path:'{out_path}' )"

    with open(out_path, "wb") as deFile:
        deFile.write(SQLITE_FILE_HEADER.encode())
        for i in range(0, len(blist), 4096):
            tblist = blist[i:i + 4096] if i > 0 else blist[16:i + 4096]
            deFile.write(AES.new(byteHmac, AES.MODE_CBC, tblist[-48:-32]).decrypt(tblist[:-48]))
            deFile.write(tblist[-48:])

    return True, [db_path, out_path, key]

@wx_core_error
def batch_decrypt(key: str, db_path: Union[str, List[str]], out_path: str, is_print: bool = False):
    """
    批量解密数据库
    :param key: 密钥 64位16进制字符串
    :param db_path: 待解密的数据库路径(文件或文件夹)
    :param out_path: 解密后的数据库输出路径(文件夹)
    :param is_logging: 是否打印日志
    :return: (bool, [[input_db_path, output_db_path, key],...])
    """
    if not isinstance(key, str) or not isinstance(out_path, str) or not os.path.exists(out_path) or len(key) != 64:
        error = f"[-] (key:'{key}' or out_path:'{out_path}') Error!"
        wx_core_loger.error(error, exc_info=True)
        return False, error

    process_list = []

    if isinstance(db_path, str):
        if not os.path.exists(db_path):
            error = f"[-] db_path:'{db_path}' not found!"
            wx_core_loger.error(error, exc_info=True)
            return False, error

        if os.path.isfile(db_path):
            inpath = db_path
            outpath = os.path.join(out_path, 'de_' + os.path.basename(db_path))
            process_list.append([key, inpath, outpath])

        elif os.path.isdir(db_path):
            for root, dirs, files in os.walk(db_path):
                for file in files:
                    inpath = os.path.join(root, file)
                    rel = os.path.relpath(root, db_path)
                    outpath = os.path.join(out_path, rel, 'de_' + file)

                    if not os.path.exists(os.path.dirname(outpath)):
                        os.makedirs(os.path.dirname(outpath))
                    process_list.append([key, inpath, outpath])
        else:
            error = f"[-] db_path:'{db_path}' Error "
            wx_core_loger.error(error, exc_info=True)
            return False, error

    elif isinstance(db_path, list):
        rt_path = os.path.commonprefix(db_path)
        if not os.path.exists(rt_path):
            rt_path = os.path.dirname(rt_path)

        for inpath in db_path:
            if not os.path.exists(inpath):
                error = f"[-] db_path:'{db_path}' not found!"
                wx_core_loger.error(error, exc_info=True)
                return False, error

            inpath = os.path.normpath(inpath)
            rel = os.path.relpath(os.path.dirname(inpath), rt_path)
            outpath = os.path.join(out_path, rel, 'de_' + os.path.basename(inpath))
            if not os.path.exists(os.path.dirname(outpath)):
                os.makedirs(os.path.dirname(outpath))
            process_list.append([key, inpath, outpath])
    else:
        error = f"[-] db_path:'{db_path}' Error "
        wx_core_loger.error(error, exc_info=True)
        return False, error

    result = []
    for i in process_list:
        result.append(decrypt(*i))  # 解密

    # 删除空文件夹
    for root, dirs, files in os.walk(out_path, topdown=False):
        for dir in dirs:
            if not os.listdir(os.path.join(root, dir)):
                os.rmdir(os.path.join(root, dir))

    if is_print:
        print("=" * 32)
        success_count = 0
        fail_count = 0
        for code, ret in result:
            if code == False:
                print(ret)
                fail_count += 1
            else:
                print(f'[+] "{ret[0]}" -> "{ret[1]}"')
                success_count += 1
        print("-" * 32)
        print(f"[+] 共 {len(result)} 个文件, 成功 {success_count} 个, 失败 {fail_count} 个")
        print("=" * 32)
    return True, result
