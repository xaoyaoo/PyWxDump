# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         simplify_wx_info.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/12/07
# -------------------------------------------------------------------------------
import hmac
import hashlib
import ctypes
import os
import winreg
import pymem
import psutil
import sys

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p


# 获取exe文件的位数
def get_exe_bit(file_path):
    """
    获取 PE 文件的位数: 32 位或 64 位
    :param file_path:  PE 文件路径(可执行文件)
    :return: 如果遇到错误则返回 64
    """
    try:
        with open(file_path, 'rb') as f:
            dos_header = f.read(2)
            if dos_header != b'MZ':
                print('get exe bit error: Invalid PE file')
                return 64
            # Seek to the offset of the PE signature
            f.seek(60)
            pe_offset_bytes = f.read(4)
            pe_offset = int.from_bytes(pe_offset_bytes, byteorder='little')

            # Seek to the Machine field in the PE header
            f.seek(pe_offset + 4)
            machine_bytes = f.read(2)
            machine = int.from_bytes(machine_bytes, byteorder='little')

            if machine == 0x14c:
                return 32
            elif machine == 0x8664:
                return 64
            else:
                print('get exe bit error: Unknown architecture: %s' % hex(machine))
                return 64
    except IOError:
        print('get exe bit error: File not found or cannot be opened')
        return 64


def pattern_scan_all(handle, pattern, *, return_multiple=False, find_num=100):
    next_region = 0
    found = []
    user_space_limit = 0x7FFFFFFF0000 if sys.maxsize > 2 ** 32 else 0x7fff0000
    while next_region < user_space_limit:
        try:
            next_region, page_found = pymem.pattern.scan_pattern_page(
                handle,
                next_region,
                pattern,
                return_multiple=return_multiple
            )
        except Exception as e:
            print(e)
            break
        if not return_multiple and page_found:
            return page_found
        if page_found:
            found += page_found
        if len(found) > find_num:
            break
    return found


def get_info_wxid(h_process):
    find_num = 100
    addrs = pattern_scan_all(h_process, br'\\Msg\\FTSContact', return_multiple=True, find_num=find_num)
    wxids = []
    for addr in addrs:
        array = ctypes.create_string_buffer(80)
        if ReadProcessMemory(h_process, void_p(addr - 30), array, 80, 0) == 0: return "None"
        array = bytes(array)  # .split(b"\\")[0]
        array = array.split(b"\\Msg")[0]
        array = array.split(b"\\")[-1]
        wxids.append(array.decode('utf-8', errors='ignore'))
    wxid = max(wxids, key=wxids.count) if wxids else "None"
    return wxid


def get_info_filePath(wxid="all"):
    if not wxid:
        return "None"
    w_dir = "MyDocument:"
    is_w_dir = False

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat", 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, "FileSavePath")
        winreg.CloseKey(key)
        w_dir = value
        is_w_dir = True
    except Exception as e:
        w_dir = "MyDocument:"

    if not is_w_dir:
        try:
            user_profile = os.environ.get("USERPROFILE")
            path_3ebffe94 = os.path.join(user_profile, "AppData", "Roaming", "Tencent", "WeChat", "All Users", "config",
                                         "3ebffe94.ini")
            with open(path_3ebffe94, "r", encoding="utf-8") as f:
                w_dir = f.read()
            is_w_dir = True
        except Exception as e:
            w_dir = "MyDocument:"

    if w_dir == "MyDocument:":
        try:
            # 打开注册表路径
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
            documents_path = winreg.QueryValueEx(key, "Personal")[0]  # 读取文档实际目录路径
            winreg.CloseKey(key)  # 关闭注册表
            documents_paths = os.path.split(documents_path)
            if "%" in documents_paths[0]:
                w_dir = os.environ.get(documents_paths[0].replace("%", ""))
                w_dir = os.path.join(w_dir, os.path.join(*documents_paths[1:]))
                # print(1, w_dir)
            else:
                w_dir = documents_path
        except Exception as e:
            profile = os.environ.get("USERPROFILE")
            w_dir = os.path.join(profile, "Documents")

    msg_dir = os.path.join(w_dir, "WeChat Files")

    if wxid == "all" and os.path.exists(msg_dir):
        return msg_dir

    filePath = os.path.join(msg_dir, wxid)
    return filePath if os.path.exists(filePath) else "None"


def get_key(pid, db_path, addr_len):
    def read_key_bytes(h_process, address, address_len=8):
        array = ctypes.create_string_buffer(address_len)
        if ReadProcessMemory(h_process, void_p(address), array, address_len, 0) == 0: return "None"
        address = int.from_bytes(array, byteorder='little')  # 逆序转换为int地址（key地址）
        key = ctypes.create_string_buffer(32)
        if ReadProcessMemory(h_process, void_p(address), key, 32, 0) == 0: return "None"
        key_bytes = bytes(key)
        return key_bytes

    def verify_key(key, wx_db_path):
        KEY_SIZE = 32
        DEFAULT_PAGESIZE = 4096
        DEFAULT_ITER = 64000
        with open(wx_db_path, "rb") as file:
            blist = file.read(5000)
        salt = blist[:16]
        byteKey = hashlib.pbkdf2_hmac("sha1", key, salt, DEFAULT_ITER, KEY_SIZE)
        first = blist[16:DEFAULT_PAGESIZE]

        mac_salt = bytes([(salt[i] ^ 58) for i in range(16)])
        mac_key = hashlib.pbkdf2_hmac("sha1", byteKey, mac_salt, 2, KEY_SIZE)
        hash_mac = hmac.new(mac_key, first[:-32], hashlib.sha1)
        hash_mac.update(b'\x01\x00\x00\x00')

        if hash_mac.digest() != first[-32:-12]:
            return False
        return True

    phone_type1 = "iphone\x00"
    phone_type2 = "android\x00"
    phone_type3 = "ipad\x00"

    pm = pymem.Pymem(pid)
    module_name = "WeChatWin.dll"

    MicroMsg_path = os.path.join(db_path, "MSG", "MicroMsg.db")

    type1_addrs = pm.pattern_scan_module(phone_type1.encode(), module_name, return_multiple=True)
    type2_addrs = pm.pattern_scan_module(phone_type2.encode(), module_name, return_multiple=True)
    type3_addrs = pm.pattern_scan_module(phone_type3.encode(), module_name, return_multiple=True)

    # print(type1_addrs, type2_addrs, type3_addrs)

    type_addrs = []
    if len(type1_addrs) >= 2: type_addrs += type1_addrs
    if len(type2_addrs) >= 2: type_addrs += type2_addrs
    if len(type3_addrs) >= 2: type_addrs += type3_addrs
    if len(type_addrs) == 0: return "None"

    type_addrs.sort()  # 从小到大排序

    for i in type_addrs[::-1]:
        for j in range(i, i - 2000, -addr_len):
            key_bytes = read_key_bytes(pm.process_handle, j, addr_len)
            if key_bytes == "None":
                continue
            if verify_key(key_bytes, MicroMsg_path):
                return key_bytes.hex()
    return "None"


# 读取微信信息(account,mobile,name,mail,wxid,key)
def read_info(is_logging=False):
    wechat_process = []
    result = []
    for process in psutil.process_iter(['name', 'exe', 'pid', 'cmdline']):
        if process.name() == 'WeChat.exe':
            wechat_process.append(process)

    if len(wechat_process) == 0:
        error = "[-] WeChat No Run"
        if is_logging: print(error)
        return error

    for process in wechat_process:
        tmp_rd = {}

        tmp_rd['pid'] = process.pid
        # tmp_rd['version'] = Dispatch("Scripting.FileSystemObject").GetFileVersion(process.exe())

        Handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, process.pid)

        addrLen = get_exe_bit(process.exe()) // 8

        tmp_rd['wxid'] = get_info_wxid(Handle)
        tmp_rd['filePath'] = get_info_filePath(tmp_rd['wxid']) if tmp_rd['wxid'] != "None" else "None"
        tmp_rd['key'] = get_key(tmp_rd['pid'], tmp_rd['filePath'], addrLen) if tmp_rd['filePath'] != "None" else "None"
        result.append(tmp_rd)


    if is_logging:
        print("=" * 32)
        if isinstance(result, str):  # 输出报错
            print(result)
        else:  # 输出结果
            for i, rlt in enumerate(result):
                for k, v in rlt.items():
                    print(f"[+] {k:>8}: {v}")
                print(end="-" * 32 + "\n" if i != len(result) - 1 else "")
        print("=" * 32)
    return result


if __name__ == '__main__':
    read_info(is_logging=True)
