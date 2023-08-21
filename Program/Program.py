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

import psutil


def get_name(pid, base_address, n_size=100):
    array = (ctypes.c_byte * n_size)()
    if ctypes.windll.kernel32.ReadProcessMemory(ctypes.c_void_p(pid), ctypes.c_void_p(base_address), array, n_size,
                                                0) == 0:
        return ""
    null_index = n_size
    for i in range(n_size):
        if array[i] == 0:
            null_index = i
            break
    text = ctypes.string_at(ctypes.byref(array), null_index).decode('utf-8', errors='ignore')

    return text


def get_account(pid, base_address, n_size=100):
    array = (ctypes.c_byte * n_size)()

    if ctypes.windll.kernel32.ReadProcessMemory(ctypes.c_void_p(pid), ctypes.c_void_p(base_address), array, n_size,
                                                0) == 0:
        return ""

    null_index = n_size
    for i in range(n_size):
        if array[i] == 0:
            null_index = i
            break
    text = ctypes.string_at(ctypes.byref(array), null_index).decode('utf-8', errors='ignore')

    return text


def get_mobile(pid, base_address, n_size=100):
    array = (ctypes.c_byte * n_size)()

    if ctypes.windll.kernel32.ReadProcessMemory(ctypes.c_void_p(pid), ctypes.c_void_p(base_address), array, n_size,
                                                0) == 0:
        return ""

    null_index = n_size
    for i in range(n_size):
        if array[i] == 0:
            null_index = i
            break
    text = ctypes.string_at(ctypes.byref(array), null_index).decode('utf-8', errors='ignore')

    return text


def get_mail(pid, base_address, n_size=100):
    array = (ctypes.c_byte * n_size)()

    if ctypes.windll.kernel32.ReadProcessMemory(ctypes.c_void_p(pid), ctypes.c_void_p(base_address), array, n_size,
                                                0) == 0:
        return ""

    null_index = n_size
    for i in range(n_size):
        if array[i] == 0:
            null_index = i
            break
    text = ctypes.string_at(ctypes.byref(array), null_index).decode('utf-8', errors='ignore')

    return text


def get_hex(h_process, lp_base_address):
    array = ctypes.create_string_buffer(8)
    if ctypes.windll.kernel32.ReadProcessMemory(h_process, ctypes.c_void_p(lp_base_address), array, 8, 0) == 0:
        return ""

    num = 32
    array2 = (ctypes.c_ubyte * num)()
    lp_base_address2 = (
            (int(binascii.hexlify(array[7]), 16) << 56) +
            (int(binascii.hexlify(array[6]), 16) << 48) +
            (int(binascii.hexlify(array[5]), 16) << 40) +
            (int(binascii.hexlify(array[4]), 16) << 32) +
            (int(binascii.hexlify(array[3]), 16) << 24) +
            (int(binascii.hexlify(array[2]), 16) << 16) +
            (int(binascii.hexlify(array[1]), 16) << 8) +
            int(binascii.hexlify(array[0]), 16)
    )

    if ctypes.windll.kernel32.ReadProcessMemory(h_process, ctypes.c_void_p(lp_base_address2), ctypes.byref(array2), num,
                                                0) == 0:
        return ""

    hex_string = binascii.hexlify(bytes(array2))
    return hex_string.decode('utf-8')


def get_file_version(file_path):
    import win32api
    info = win32api.GetFileVersionInfo(file_path, "\\")
    ms = info['FileVersionMS']
    ls = info['FileVersionLS']
    file_version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
    # version = parse(file_version)
    return file_version


def read_test(version_list):
    support_list = None
    wechat_process = None

    rd = []

    for process in psutil.process_iter(['name', 'exe', 'pid', 'cmdline']):
        if process.info['name'] == 'WeChat.exe':
            tmp_rd = {}
            wechat_process = process
            tmp_rd['pid'] = wechat_process.pid
            # print("[+] WeChatProcessPID: " + str(wechat_process.info['pid']))
            wechat_win_base_address = 0
            for module in wechat_process.memory_maps(grouped=False):
                if module.path and 'WeChatWin.dll' in module.path:
                    wechat_win_base_address = module.addr
                    wechat_win_base_address = int(wechat_win_base_address, 16)
                    file_version = get_file_version(module.path)
                    file_version_str = str(file_version)

                    tmp_rd['version'] = file_version_str

                    # print("[+] WeChatVersion: " + file_version_str)

                    if file_version_str not in version_list:
                        return "[-] WeChat Current Version Is: " + file_version_str + " Not Supported"
                    else:
                        support_list = version_list[file_version_str]
                        support_list = list(support_list)
                    break
            Handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, wechat_process.pid)
            if support_list is None:
                return "[-] WeChat Base Address Get Failed"
            else:
                wechat_key = wechat_win_base_address + support_list[4]

                hex_key = get_hex(Handle, wechat_key)
                tmp_rd['key'] = hex_key.strip()

                if hex_key.strip() == "":
                    return "[-] WeChat Is Running, But Maybe Not Logged In"
                else:
                    wechat_name = wechat_win_base_address + support_list[0]
                    tmp_rd['name'] = get_name(Handle, wechat_name, 100).strip()

                    wechat_account = wechat_win_base_address + support_list[1]
                    account = get_account(Handle, wechat_account, 100).strip()
                    if account.strip() == "":
                        tmp_rd['account'] = "None"
                    else:
                        tmp_rd['account'] = account

                    wechat_mobile = wechat_win_base_address + support_list[2]
                    mobile = get_mobile(Handle, wechat_mobile, 100).strip()
                    if mobile.strip() == "":
                        tmp_rd['mobile'] = "None"
                    else:
                        tmp_rd['mobile'] = mobile

                    wechat_mail = wechat_win_base_address + support_list[3]
                    mail = get_mail(Handle, wechat_mail, 100).strip()
                    if mail.strip() != "":
                        tmp_rd['mail'] = mail
                    else:
                        tmp_rd['mail'] = "None"

            rd.append(tmp_rd)

    if wechat_process is None:
        return "[-] WeChat No Run"
    return rd

if __name__ == "__main__":
    version_list = json.load(open("version_list.json", "r", encoding="utf-8"))
    rd = read_test(version_list)
    for i in rd:
        for k, v in i.items():
            print(f"[+] {k}: {v}")

        print("=====================================")
