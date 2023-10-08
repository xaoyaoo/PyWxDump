# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         getwxinfo.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/08/21
# -------------------------------------------------------------------------------
import binascii
import json
import ctypes
import win32api
import psutil

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p


def get_info_without_key(pid, address, n_size=64):
    array = ctypes.create_string_buffer(n_size)
    if ReadProcessMemory(void_p(pid), void_p(address), array, n_size, 0) == 0: return "None"
    array = bytes(array).split(b"\x00")[0] if b"\x00" in array else bytes(array)
    text = array.decode('utf-8', errors='ignore')
    return text.strip() if text.strip() != "" else "None"


def get_key(h_process, address):
    array = ctypes.create_string_buffer(8)
    if ReadProcessMemory(h_process, void_p(address), array, 8, 0) == 0: return "None"
    key = ctypes.create_string_buffer(32)
    address = int.from_bytes(array, byteorder='little')  # 逆序转换为int地址（key地址）
    if ReadProcessMemory(h_process, void_p(address), key, 32, 0) == 0: return "None"
    key_string = bytes(key).hex()
    return key_string


def get_file_version(file_path):
    info = win32api.GetFileVersionInfo(file_path, "\\")
    ms,ls = info['FileVersionMS'],info['FileVersionLS']
    file_version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
    return file_version


def read_info(version_list):
    support_list = None
    wechat_process = []
    result = []

    for process in psutil.process_iter(['name', 'exe', 'pid', 'cmdline']):
        if process.name() == 'WeChat.exe':
            wechat_process.append(process)

    if len(wechat_process) == 0:
        return "[-] WeChat No Run"

    for process in wechat_process:
        tmp_rd = {}
        tmp_rd['pid'] = process.pid

        wechat_base_address = 0
        for module in process.memory_maps(grouped=False):
            if module.path and 'WeChatWin.dll' in module.path:
                wechat_base_address = int(module.addr, 16)
                tmp_rd['version'] = get_file_version(module.path)
                support_list = version_list.get(tmp_rd['version'], None)
                break

        if wechat_base_address == 0:
            return f"[-] WeChat WeChatWin.dll Not Found"
        if not isinstance(support_list, list):
            return f"[-] WeChat Current Version {tmp_rd['version']} Is Not Supported"

        Handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, process.pid)

        name_baseaddr = wechat_base_address + support_list[0]
        account__baseaddr = wechat_base_address + support_list[1]
        mobile_baseaddr = wechat_base_address + support_list[2]
        mail_baseaddr = wechat_base_address + support_list[3]
        key_baseaddr = wechat_base_address + support_list[4]

        tmp_rd['account'] = get_info_without_key(Handle, account__baseaddr, 32)
        tmp_rd['mobile'] = get_info_without_key(Handle, mobile_baseaddr, 64)
        tmp_rd['name'] = get_info_without_key(Handle, name_baseaddr, 64)
        tmp_rd['mail'] = get_info_without_key(Handle, mail_baseaddr, 64) if support_list[3] != 0 else "None"
        tmp_rd['key'] = get_key(Handle, key_baseaddr)
        result.append(tmp_rd)

    return result


if __name__ == "__main__":
    version_list = json.load(open("version_list.json", "r", encoding="utf-8"))
    result = read_info(version_list)
    if isinstance(result, str):
        print(result)
    else:
        print("=" * 32)
        for i in result:
            for k, v in i.items():
                print(f"[+] {k:>7}: {v}")
            print("=" * 32)
