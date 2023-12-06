# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         getwxinfo.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/08/21
# -------------------------------------------------------------------------------
import json
import ctypes
import os
import re
import winreg
import pymem
from win32com.client import Dispatch
import psutil
import sys
from typing import List, Union

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p


# 读取内存中的字符串(非key部分)
def get_info_without_key(h_process, address, n_size=64):
    array = ctypes.create_string_buffer(n_size)
    if ReadProcessMemory(h_process, void_p(address), array, n_size, 0) == 0: return "None"
    array = bytes(array).split(b"\x00")[0] if b"\x00" in array else bytes(array)
    text = array.decode('utf-8', errors='ignore')
    return text.strip() if text.strip() != "" else "None"


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
    # find_num = 1000
    # addrs = pattern_scan_all(h_process, br'\\FileStorage', return_multiple=True, find_num=find_num)
    # wxids = []
    # for addr in addrs:
    #     array = ctypes.create_string_buffer(33)
    #     if ReadProcessMemory(h_process, void_p(addr - 21), array, 33, 0) == 0: return "None"
    #     array = bytes(array)  # .decode('utf-8', errors='ignore')
    #     array = array.split(br'\FileStorage')[0]
    #     for part in [b'}', b'\x7f', b'\\']:
    #         if part in array:
    #             array = array.split(part)[1]
    #             wxids.append(array.decode('utf-8', errors='ignore'))
    #             break
    # wxid = max(wxids, key=wxids.count) if wxids else "None"

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
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat", 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, "FileSavePath")
        winreg.CloseKey(key)
        w_dir = value
        print(0, w_dir)
    except Exception as e:
        # 获取文档实际目录
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
                print(1, w_dir)
            else:
                w_dir = documents_path
                print(2, w_dir)
        except Exception as e:
            profile = os.environ.get("USERPROFILE")  # 获取用户目录
            w_dir = os.path.join(profile, "Documents")
            print(3, w_dir)
    if w_dir == "MyDocument:":
        profile = os.environ.get("USERPROFILE")
        w_dir = os.path.join(profile, "Documents")
    msg_dir = os.path.join(w_dir, "WeChat Files")
    print(msg_dir)
    if wxid == "all" and os.path.exists(msg_dir):
        return msg_dir

    filePath = os.path.join(msg_dir, wxid)
    return filePath if os.path.exists(filePath) else "None"


# 读取内存中的key
def get_key(h_process, address, address_len=8):
    array = ctypes.create_string_buffer(address_len)
    if ReadProcessMemory(h_process, void_p(address), array, address_len, 0) == 0: return "None"
    address = int.from_bytes(array, byteorder='little')  # 逆序转换为int地址（key地址）
    key = ctypes.create_string_buffer(32)
    if ReadProcessMemory(h_process, void_p(address), key, 32, 0) == 0: return "None"
    key_string = bytes(key).hex()
    return key_string


# 读取微信信息(account,mobile,name,mail,wxid,key)
def read_info(version_list, is_logging=False):
    wechat_process = []
    result = []
    error = ""
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
        tmp_rd['version'] = Dispatch("Scripting.FileSystemObject").GetFileVersion(process.exe())

        bias_list = version_list.get(tmp_rd['version'], None)
        if not isinstance(bias_list, list):
            error = f"[-] WeChat Current Version {tmp_rd['version']} Is Not Supported"
            if is_logging: print(error)
            return error

        wechat_base_address = 0
        for module in process.memory_maps(grouped=False):
            if module.path and 'WeChatWin.dll' in module.path:
                wechat_base_address = int(module.addr, 16)
                break
        if wechat_base_address == 0:
            error = f"[-] WeChat WeChatWin.dll Not Found"
            if is_logging: print(error)
            return error

        Handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, process.pid)

        name_baseaddr = wechat_base_address + bias_list[0]
        account__baseaddr = wechat_base_address + bias_list[1]
        mobile_baseaddr = wechat_base_address + bias_list[2]
        mail_baseaddr = wechat_base_address + bias_list[3]
        key_baseaddr = wechat_base_address + bias_list[4]

        addrLen = 4 if tmp_rd['version'] in ["3.9.2.23", "3.9.2.26"] else 8

        tmp_rd['account'] = get_info_without_key(Handle, account__baseaddr, 32) if bias_list[1] != 0 else "None"
        tmp_rd['mobile'] = get_info_without_key(Handle, mobile_baseaddr, 64) if bias_list[2] != 0 else "None"
        tmp_rd['name'] = get_info_without_key(Handle, name_baseaddr, 64) if bias_list[0] != 0 else "None"
        tmp_rd['mail'] = get_info_without_key(Handle, mail_baseaddr, 64) if bias_list[3] != 0 else "None"
        tmp_rd['wxid'] = get_info_wxid(Handle)
        tmp_rd['filePath'] = get_info_filePath(tmp_rd['wxid'])
        tmp_rd['key'] = get_key(Handle, key_baseaddr, addrLen) if bias_list[4] != 0 else "None"
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


def get_wechat_db(require_list: Union[List[str], str] = "all", msg_dir: str = None, wxid: Union[List[str], str] = None,
                  is_logging: bool = False):
    if not msg_dir:
        msg_dir = get_info_filePath(wxid="all")

    if not os.path.exists(msg_dir):
        error = f"[-] 目录不存在: {msg_dir}"
        if is_logging: print(error)
        return error

    user_dirs = {}  # wx用户目录
    files = os.listdir(msg_dir)
    if wxid:  # 如果指定wxid
        if isinstance(wxid, str):
            wxid = wxid.split(";")
        for file_name in files:
            if file_name in wxid:
                user_dirs[os.path.join(msg_dir, file_name)] = os.path.join(msg_dir, file_name)
    else:  # 如果未指定wxid
        for file_name in files:
            if file_name == "All Users" or file_name == "Applet" or file_name == "WMPF":
                continue
            user_dirs[os.path.join(msg_dir, file_name)] = os.path.join(msg_dir, file_name)

    if isinstance(require_list, str):
        require_list = require_list.split(";")

    # generate pattern
    if "all" in require_list:
        pattern = {"all": re.compile(r".*\.db$")}
    elif isinstance(require_list, list):
        pattern = {}
        for require in require_list:
            pattern[require] = re.compile(r"%s.*\.db$" % require)
    else:
        error = f"[-] 参数错误: {require_list}"
        if is_logging: print(error)
        return error

    # 获取数据库路径
    for user, user_dir in user_dirs.items():  # 遍历用户目录
        user_dirs[user] = {n: [] for n in pattern.keys()}
        for root, dirs, files in os.walk(user_dir):
            for file_name in files:
                for n, p in pattern.items():
                    if p.match(file_name):
                        src_path = os.path.join(root, file_name)
                        user_dirs[user][n].append(src_path)

    if is_logging:
        for user, user_dir in user_dirs.items():
            print(f"[+] user_path: {user}")
            for n, paths in user_dir.items():
                print(f"    {n}:")
                for path in paths:
                    print(f"        {path.replace(user, '')}")
        print("-" * 32)
        print(f"[+] 共 {len(user_dirs)} 个微信账号")

    return user_dirs


if __name__ == '__main__':
    with open("version_list.json", "r", encoding="utf-8") as f:
        version_list = json.load(f)
    read_info(version_list, is_logging=True)
