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


# def get_pid(keyword):
#     """
#     获取进程id
#     :param keyword: 关键字
#     :return:
#     """
#     pids = {}
#     for proc in psutil.process_iter():
#         if keyword in proc.name():
#             pids[proc.pid] = proc
#     return pids
#
#
# class BaseAddr:
#     def __init__(self, pid, proc_module_name="WeChatWin.dll"):
#         self.pid = pid
#         self.module_name = proc_module_name
#         self.proc = psutil.Process(self.pid)
#         self.version = self.get_app_version(self.proc.exe())
#         self.base_address = 0
#         self.end_address = 0
#         self.batch = 0
#
#         self.key_start_addr = 0
#         self.key_end_addr = 0
#
#         self.mobile_addr = []
#         self.name_addr = []
#         self.account_addr = []
#         # self.key_addr = []
#
#         self.get_base_addr()
#
#     def get_app_version(self, executable_path):
#         info = win32api.GetFileVersionInfo(executable_path, "\\")
#         version = info['FileVersionMS'] >> 16, info['FileVersionMS'] & 0xFFFF, \
#                   info['FileVersionLS'] >> 16, info['FileVersionLS'] & 0xFFFF
#         version_str = ".".join(map(str, version))
#
#         return version_str
#
#     def get_base_addr(self):
#         """
#         获取模块基址
#         :param pid: 进程id
#         :param module_name: 模块名
#         :return:
#         """
#         base_address = 0
#         end_address = 0
#         batch = 0
#         n = 0
#         for module in self.proc.memory_maps(grouped=False):
#             if self.module_name in module.path:
#                 if n == 0:
#                     base_address = int(module.addr, 16)
#                     batch = module.rss
#                 n += 1
#                 end_address = int(module.addr, 16) + module.rss
#
#         self.base_address = base_address
#         self.end_address = end_address
#         self.batch = batch
#         # self.batch = end_address - base_address
#
#     def find_all(self, c, string):
#         """
#         查找字符串中所有子串的位置
#         :param c: 子串 b'123'
#         :param string: 字符串 b'123456789123'
#         :return:
#         """
#         return [m.start() for m in re.finditer(re.escape(c), string)]
#
#     # 搜索内存地址范围内的值
#     def search_memory_value(self, mobile, name, account):
#         mobile = mobile.encode("utf-8")
#         name = name.encode("utf-8")
#         account = account.encode("utf-8")
#
#         Handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, self.pid)
#
#         mobile_addr = []
#         name_addr = []
#         account_addr = []
#
#         array = ctypes.create_string_buffer(self.batch)
#         for i in range(self.base_address, self.end_address, self.batch):
#             if ReadProcessMemory(Handle, void_p(i), array, self.batch, None) == 0:
#                 continue
#
#             hex_string = array.raw  # 读取到的内存数据
#
#             if mobile in hex_string:
#                 mobile_addr = mobile_addr + [m.start() + i for m in re.finditer(re.escape(mobile), hex_string)]
#             if name in hex_string:
#                 name_addr = name_addr + [m.start() + i for m in re.finditer(re.escape(name), hex_string)]
#             if account in hex_string:
#                 account_addr = account_addr + [m.start() + i for m in re.finditer(re.escape(account), hex_string)]
#
#         self.mobile_addr = mobile_addr
#         self.name_addr = name_addr
#         self.account_addr = account_addr
#         return mobile_addr, name_addr, account_addr
#
#     def get_key_addr(self, key):
#         """
#         获取key的地址
#         :param key:
#         :return:
#         """
#         key = bytes.fromhex(key)
#
#         module_start_addr = 34199871460642
#         module_end_addr = 0
#         for module in self.proc.memory_maps(grouped=False):
#             if "WeChat" in module.path:
#                 start_addr = int(module.addr, 16)
#                 end_addr = start_addr + module.rss
#
#                 if module_start_addr > start_addr:
#                     module_start_addr = start_addr
#                 if module_end_addr < end_addr:
#                     module_end_addr = end_addr
#
#         Handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, self.pid)
#         array = ctypes.create_string_buffer(self.batch)
#         for i in range(module_start_addr, module_end_addr, self.batch):
#             if ReadProcessMemory(Handle, void_p(i), array, self.batch, None) == 0:
#                 continue
#
#             hex_string = array.raw  # 读取到的内存数据
#             if key in hex_string:
#                 self.key_addr_tmp = i + hex_string.find(key)
#                 break
#             if ((i - module_start_addr) / self.batch) > 300000:
#                 self.key_addr = 0
#                 return -1
#
#         array_key = []
#         for i in range(8):
#             byte_value = (self.key_addr_tmp >> (i * 8)) & 0xFF
#             hex_string = format(byte_value, '02x')
#             byte_obj = bytes.fromhex(hex_string)
#             array_key.append(byte_obj)
#         # 合并数组
#         array_key = b''.join(array_key)
#
#         array = ctypes.create_string_buffer(self.batch)
#         for i in range(self.base_address, self.end_address, self.batch):
#             if ReadProcessMemory(Handle, void_p(i), array, self.batch, None) == 0:
#                 continue
#
#             hex_string = array.raw  # 读取到的内存数据
#             if array_key in hex_string:
#                 self.key_addr = i + hex_string.find(array_key)
#                 return self.key_addr
#
#     def calculate_offset(self, addr):
#         """
#         计算偏移量
#         :param addr:
#         :return:
#         """
#         if addr == 0:
#             return 0
#         offset = addr - self.base_address
#         return offset
#
#     def get_offset(self):
#         """
#         计算偏移量
#         :param addr:
#         :return:
#         """
#         mobile_offset = 0
#         name_offset = 0
#         account_offset = 0
#         key_offset = 0
#         if len(self.mobile_addr) >= 1:
#             mobile_offset = self.calculate_offset(self.mobile_addr[0])
#         if len(self.name_addr) >= 1:
#             name_offset = self.calculate_offset(self.name_addr[0])
#         if len(self.account_addr) >= 1:
#             if len(self.account_addr) >= 2:
#                 account_offset = self.calculate_offset(self.account_addr[1])
#             else:
#                 account_offset = self.calculate_offset(self.account_addr[0])
#
#         key_offset = self.calculate_offset(self.key_addr)
#
#         self.key_offset = key_offset
#         self.mobile_offset = mobile_offset
#         self.name_offset = name_offset
#         self.account_offset = account_offset
#         return name_offset, account_offset, mobile_offset, 0, key_offset
#
#
# def run(mobile, name, account, key):
#     proc_name = "WeChat.exe"
#     proc_module_name = "WeChatWin.dll"
#
#     pids = get_pid(proc_name)
#     for pid, proc in pids.items():
#         ba = BaseAddr(pid, proc_module_name)
#         ba.search_memory_value(mobile, name, account)
#         ba.get_key_addr(key)
#         name_offset, account_offset, mobile_offset, _, key_offset = ba.get_offset()
#         rdata = {ba.version: [name_offset, account_offset, mobile_offset, 0, key_offset]}
#         return rdata


class BaseAddr:
    def __init__(self, account, mobile, name, key):
        self.account = account.encode("utf-8")
        self.mobile = mobile.encode("utf-8")
        self.name = name.encode("utf-8")
        self.key = bytes.fromhex(key)

        self.process_name = "WeChat.exe"
        self.module_name = "WeChatWin.dll"

        self.pm = Pymem("WeChat.exe")

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

        key = key_addr.to_bytes(8, byteorder='little')
        result = self.search_memory_value(key, self.module_name)
        return result

    def run(self):
        self.version = self.get_file_version(self.process_name)
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
