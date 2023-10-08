# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         get_base_addr.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/08/22
# -------------------------------------------------------------------------------
import argparse
import ctypes
import json
import re
import time

import psutil
import win32api
from pymem import Pymem
import pymem

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p


class BaseAddr:
    def __init__(self, account, mobile, name, key):
        self.account = account.encode("utf-8")
        self.mobile = mobile.encode("utf-8")
        self.name = name.encode("utf-8")
        self.key = bytes.fromhex(key)

        self.process_name = "WeChat.exe"
        self.module_name = "WeChatWin.dll"

        self.pm = Pymem("WeChat.exe")

        self.islogin = True

    def find_all(self, c: bytes, string: bytes, base_addr=0):
        """
        查找字符串中所有子串的位置
        :param c: 子串 b'123'
        :param string: 字符串 b'123456789123'
        :return:
        """
        return [base_addr + m.start() for m in re.finditer(re.escape(c), string)]

    def get_file_version(self, process_name):
        for process in psutil.process_iter(['name', 'exe', 'pid', 'cmdline']):
            if process.name() == process_name:
                file_path = process.exe()
                info = win32api.GetFileVersionInfo(file_path, "\\")
                ms, ls = info['FileVersionMS'], info['FileVersionLS']
                file_version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
                return file_version
        self.islogin = False

    def search_memory_value(self, value: bytes, module_name="WeChatWin.dll"):
        # 创建 Pymem 对象
        pm = self.pm
        module = pymem.process.module_from_name(pm.process_handle, module_name)
        mem_data = pm.read_bytes(module.lpBaseOfDll, module.SizeOfImage)
        result = self.find_all(value, mem_data)
        result = result[-1] if len(result) > 0 else 0
        return result

    def search_key(self, key: bytes):
        pid = self.pm.process_id
        # print(self.pm.process_base.lpBaseOfDll, self.pm.process_base.SizeOfImage)

        batch = 4096

        module_start_addr = 34199871460642
        module_end_addr = 0
        for process in psutil.process_iter(['name', 'exe', 'pid', 'cmdline']):
            if process.name() == self.process_name:
                for module in process.memory_maps(grouped=False):
                    if "WeChat" in module.path:
                        start_addr = int(module.addr, 16)
                        end_addr = start_addr + module.rss

                        if module_start_addr > start_addr:
                            module_start_addr = start_addr
                        if module_end_addr < end_addr:
                            module_end_addr = end_addr

        Handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
        array = ctypes.create_string_buffer(batch)
        key_addr = 0
        for i in range(module_start_addr, module_end_addr, batch):
            if ReadProcessMemory(Handle, void_p(i), array, batch, None) == 0:
                continue
            hex_string = array.raw  # 读取到的内存数据
            key_addr = self.find_all(key, hex_string, i)
            if len(key_addr) > 0:
                key_addr = key_addr[0]
                break
        # print(key_addr)
        key = key_addr.to_bytes(8, byteorder='little')
        result = self.search_memory_value(key, self.module_name)
        return result

    def run(self):
        self.version = self.get_file_version(self.process_name)
        if not self.islogin:
            return "[-] WeChat No Run"
        key_bias = self.search_key(self.key)
        mobile_bias = self.search_memory_value(self.mobile)
        name_bias = self.search_memory_value(self.name)
        account_bias = self.search_memory_value(self.account)
        return {self.version: [name_bias, account_bias, mobile_bias, 0, key_bias]}


if __name__ == '__main__':
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser()
    parser.add_argument("--mobile", type=str, help="手机号")
    parser.add_argument("--name", type=str, help="微信昵称")
    parser.add_argument("--account", type=str, help="微信账号")
    parser.add_argument("--key", type=str, help="密钥")

    # 解析命令行参数
    args = parser.parse_args()

    # 检查是否缺少必要参数，并抛出错误
    if not args.mobile or not args.name or not args.account or not args.key:
        raise ValueError("缺少必要的命令行参数！请提供手机号、微信昵称、微信账号和密钥。")

    # 从命令行参数获取值
    mobile = args.mobile
    name = args.name
    account = args.account
    key = args.key

    # 调用 run 函数，并传入参数
    # rdata = run(mobile, name, account, key)
    # print(rdata)
    rdata = BaseAddr(account, mobile, name, key).run()

    print(rdata)

    # 添加到version_list.json
    with open("version_list.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        data.update(rdata)
    with open("version_list.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
