# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         get_base_addr.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/08/22
# -------------------------------------------------------------------------------
import ctypes
import json
import os
import re
import sys
import psutil
import pymem

from .utils import get_exe_version, get_exe_bit, verify_key

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p


class BiasAddr:
    def __init__(self, account, mobile, name, key, db_path):
        self.account = account.encode("utf-8")
        self.mobile = mobile.encode("utf-8")
        self.name = name.encode("utf-8")
        self.key = bytes.fromhex(key) if key else b""
        self.db_path = db_path if db_path and os.path.exists(db_path) else ""

        self.process_name = "WeChat.exe"
        self.module_name = "WeChatWin.dll"

        self.pm = None  # Pymem 对象
        self.is_WoW64 = None  # True: 32位进程运行在64位系统上 False: 64位进程运行在64位系统上
        self.process_handle = None  # 进程句柄
        self.pid = None  # 进程ID
        self.version = None  # 微信版本号
        self.process = None  # 进程对象
        self.exe_path = None  # 微信路径
        self.address_len = None  # 4 if self.bits == 32 else 8  # 4字节或8字节
        self.bits = 64 if sys.maxsize > 2 ** 32 else 32  # 系统：32位或64位

    def get_process_handle(self):
        try:
            self.pm = pymem.Pymem(self.process_name)
            self.pm.check_wow64()
            self.is_WoW64 = self.pm.is_WoW64
            self.process_handle = self.pm.process_handle
            self.pid = self.pm.process_id
            self.process = psutil.Process(self.pid)
            self.exe_path = self.process.exe()
            self.version = get_exe_version(self.exe_path)

            version_nums = list(map(int, self.version.split(".")))  # 将版本号拆分为数字列表
            if version_nums[0] <= 3 and version_nums[1] <= 9 and version_nums[2] <= 2:
                self.address_len = 4
            else:
                self.address_len = 8
            return True, ""
        except pymem.exception.ProcessNotFound:
            return False, "[-] WeChat No Run"

    def search_memory_value(self, value: bytes, module_name="WeChatWin.dll"):
        # 创建 Pymem 对象
        module = pymem.process.module_from_name(self.pm.process_handle, module_name)
        ret = self.pm.pattern_scan_module(value, module, return_multiple=True)
        ret = ret[-1] - module.lpBaseOfDll if len(ret) > 0 else 0
        return ret

    def get_key_bias1(self):
        """
        2024.01.26 wx version：3.9.9.35 失效
        :return:
        """
        try:
            byteLen = self.address_len  # 4 if self.bits == 32 else 8  # 4字节或8字节

            keyLenOffset = 0x8c if self.bits == 32 else 0xd0
            keyWindllOffset = 0x90 if self.bits == 32 else 0xd8

            module = pymem.process.module_from_name(self.process_handle, self.module_name)
            keyBytes = b'-----BEGIN PUBLIC KEY-----\n...'
            publicKeyList = pymem.pattern.pattern_scan_all(self.process_handle, keyBytes, return_multiple=True)

            keyaddrs = []
            for addr in publicKeyList:
                keyBytes = addr.to_bytes(byteLen, byteorder="little", signed=True)  # 低位在前
                may_addrs = pymem.pattern.pattern_scan_module(self.process_handle, module, keyBytes,
                                                              return_multiple=True)
                if may_addrs != 0 and len(may_addrs) > 0:
                    for addr in may_addrs:
                        keyLen = self.pm.read_uchar(addr - keyLenOffset)
                        if keyLen != 32:
                            continue
                        keyaddrs.append(addr - keyWindllOffset)

            return keyaddrs[-1] - module.lpBaseOfDll if len(keyaddrs) > 0 else 0
        except:
            return 0

    def search_key(self, key: bytes):
        key = re.escape(key)  # 转义特殊字符
        key_addr = self.pm.pattern_scan_all(key, return_multiple=False)
        key = key_addr.to_bytes(self.address_len, byteorder='little', signed=True)
        result = self.search_memory_value(key, self.module_name)
        return result

    def get_key_bias2(self, wx_db_path):

        addr_len = get_exe_bit(self.exe_path) // 8
        db_path = wx_db_path

        def read_key_bytes(h_process, address, address_len=8):
            array = ctypes.create_string_buffer(address_len)
            if ReadProcessMemory(h_process, void_p(address), array, address_len, 0) == 0: return "None"
            address = int.from_bytes(array, byteorder='little')  # 逆序转换为int地址（key地址）
            key = ctypes.create_string_buffer(32)
            if ReadProcessMemory(h_process, void_p(address), key, 32, 0) == 0: return "None"
            key_bytes = bytes(key)
            return key_bytes

        phone_type1 = "iphone\x00"
        phone_type2 = "android\x00"
        phone_type3 = "ipad\x00"

        pm = pymem.Pymem(self.pid)
        module_name = "WeChatWin.dll"

        MicroMsg_path = os.path.join(db_path, "MSG", "MicroMsg.db")

        type1_addrs = pm.pattern_scan_module(phone_type1.encode(), module_name, return_multiple=True)
        type2_addrs = pm.pattern_scan_module(phone_type2.encode(), module_name, return_multiple=True)
        type3_addrs = pm.pattern_scan_module(phone_type3.encode(), module_name, return_multiple=True)

        type_addrs = []
        if len(type1_addrs) >= 2: type_addrs += type1_addrs
        if len(type2_addrs) >= 2: type_addrs += type2_addrs
        if len(type3_addrs) >= 2: type_addrs += type3_addrs
        if len(type_addrs) == 0: return "None"

        type_addrs.sort()  # 从小到大排序

        module = pymem.process.module_from_name(pm.process_handle, module_name)

        for i in type_addrs[::-1]:
            for j in range(i, i - 2000, -addr_len):
                key_bytes = read_key_bytes(pm.process_handle, j, addr_len)
                if key_bytes == "None":
                    continue
                if verify_key(key_bytes, MicroMsg_path):
                    return j - module.lpBaseOfDll
        return 0

    def run(self, logging_path=False, version_list_path=None):
        if not self.get_process_handle()[0]:
            return None
        mobile_bias = self.search_memory_value(self.mobile, self.module_name)
        name_bias = self.search_memory_value(self.name, self.module_name)
        account_bias = self.search_memory_value(self.account, self.module_name)
        key_bias = 0
        key_bias = self.get_key_bias1() if key_bias <= 0 else key_bias
        key_bias = self.search_key(self.key) if key_bias <= 0 and self.key else key_bias
        key_bias = self.get_key_bias2(self.db_path) if key_bias <= 0 and self.db_path else key_bias

        rdata = {self.version: [name_bias, account_bias, mobile_bias, 0, key_bias]}

        if version_list_path and os.path.exists(version_list_path):
            with open(version_list_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                data.update(rdata)
            with open(version_list_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        if os.path.exists(logging_path) and isinstance(logging_path, str):
            with open(logging_path, "a", encoding="utf-8") as f:
                f.write("{版本号:昵称,账号,手机号,邮箱,KEY}" + "\n")
                f.write(str(rdata) + "\n")
        elif logging_path:
            print("{版本号:昵称,账号,手机号,邮箱,KEY}")
            print(rdata)
        return rdata


if __name__ == '__main__':
    account, mobile, name, key, db_path = "test", "test", "test", None, r"test"
    bias_addr = BiasAddr(account, mobile, name, key, db_path)
    bias_addr.run(logging_path=True)
