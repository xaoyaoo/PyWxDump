# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         getwxinfo.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/08/21
# -------------------------------------------------------------------------------
import ctypes
import json
import os
import re
import winreg
import psutil
import pymem
from typing import List, Union
from .utils import pattern_scan_all, verify_key, get_exe_version, get_exe_bit, info_error

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p


# 读取内存中的字符串(key部分)
@info_error
def get_info_with_key(h_process, address, address_len=8):
    array = ctypes.create_string_buffer(address_len)
    if ReadProcessMemory(h_process, void_p(address), array, address_len, 0) == 0: return "None"
    address = int.from_bytes(array, byteorder='little')  # 逆序转换为int地址（key地址）
    key = ctypes.create_string_buffer(32)
    if ReadProcessMemory(h_process, void_p(address), key, 32, 0) == 0: return "None"
    key_string = bytes(key).hex()
    return key_string


# 读取内存中的字符串(非key部分)
@info_error
def get_info_string(h_process, address, n_size=64):
    array = ctypes.create_string_buffer(n_size)
    if ReadProcessMemory(h_process, void_p(address), array, n_size, 0) == 0: return "None"
    array = bytes(array).split(b"\x00")[0] if b"\x00" in array else bytes(array)
    text = array.decode('utf-8', errors='ignore')
    return text.strip() if text.strip() != "" else "None"


# 读取内存中的字符串(昵称部分name)
@info_error
def get_info_name(h_process, address, address_len=8, n_size=64):
    array = ctypes.create_string_buffer(n_size)
    if ReadProcessMemory(h_process, void_p(address), array, n_size, 0) == 0: return "None"
    address1 = int.from_bytes(array[:address_len], byteorder='little')  # 逆序转换为int地址（key地址）
    info_name = get_info_string(h_process, address1, n_size)
    if info_name != "None":
        return info_name
    array = bytes(array).split(b"\x00")[0] if b"\x00" in array else bytes(array)
    text = array.decode('utf-8', errors='ignore')
    return text.strip() if text.strip() != "" else "None"


# 读取内存中的wxid
@info_error
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


# 读取内存中的filePath基于wxid（慢）
@info_error
def get_info_filePath_base_wxid(h_process, wxid=""):
    find_num = 10
    addrs = pattern_scan_all(h_process, wxid.encode() + br'\\Msg\\FTSContact', return_multiple=True, find_num=find_num)
    filePath = []
    for addr in addrs:
        win_addr_len = 260
        array = ctypes.create_string_buffer(win_addr_len)
        if ReadProcessMemory(h_process, void_p(addr - win_addr_len + 50), array, win_addr_len, 0) == 0: return "None"
        array = bytes(array).split(b"\\Msg")[0]
        array = array.split(b"\00")[-1]
        filePath.append(array.decode('utf-8', errors='ignore'))
    filePath = max(filePath, key=filePath.count) if filePath else "None"
    return filePath


@info_error
def get_info_filePath(wxid="all"):
    """
    # 读取filePath (微信文件路径) （快）
    :param wxid: 微信id
    :return: 返回filePath
    """
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


@info_error
def get_key(pid, db_path, addr_len):
    """
    获取key （慢）
    :param pid: 进程id
    :param db_path: 微信数据库路径
    :param addr_len: 地址长度
    :return: 返回key
    """

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


def get_details(process, version_list: dict = None, is_logging: bool = False):
    rd = {'pid': process.pid, 'version': get_exe_version(process.exe()),
          "account": "None", "mobile": "None", "name": "None", "mail": "None",
          "wxid": "None", "key": "None", "filePath": "None"}
    try:
        Handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, process.pid)

        bias_list = version_list.get(rd['version'], None)

        addrLen = get_exe_bit(process.exe()) // 8
        if not isinstance(bias_list, list) or len(bias_list) <= 4:
            error = f"[-] WeChat Current Version Is Not Supported(maybe not get account,mobile,name,mail)"
            if is_logging: print(error)
        else:
            wechat_base_address = 0
            for module in process.memory_maps(grouped=False):
                if module.path and 'WeChatWin.dll' in module.path:
                    wechat_base_address = int(module.addr, 16)
                    rd['version'] = get_exe_version(module.path) if os.path.exists(module.path) else rd['version']
                    break
            if wechat_base_address == 0:
                error = f"[-] WeChat WeChatWin.dll Not Found"
                if is_logging: print(error)
                # return error

            name_baseaddr = wechat_base_address + bias_list[0]
            account__baseaddr = wechat_base_address + bias_list[1]
            mobile_baseaddr = wechat_base_address + bias_list[2]
            mail_baseaddr = wechat_base_address + bias_list[3]
            key_baseaddr = wechat_base_address + bias_list[4]

            rd['account'] = get_info_string(Handle, account__baseaddr, 32) if bias_list[1] != 0 else "None"
            rd['mobile'] = get_info_string(Handle, mobile_baseaddr, 64) if bias_list[2] != 0 else "None"
            rd['name'] = get_info_name(Handle, name_baseaddr, addrLen, 64) if bias_list[0] != 0 else "None"
            rd['mail'] = get_info_string(Handle, mail_baseaddr, 64) if bias_list[3] != 0 else "None"
            rd['key'] = get_info_with_key(Handle, key_baseaddr, addrLen) if bias_list[4] != 0 else "None"

        rd['wxid'] = get_info_wxid(Handle)

        rd['filePath'] = get_info_filePath(rd['wxid']) if rd['wxid'] != "None" else "None"
        if rd['wxid'] != "None" and rd['filePath'] == "None":  # 通过wxid获取filePath,如果filePath为空则通过wxid获取filePath
            rd['filePath'] = get_info_filePath_base_wxid(Handle, rd['wxid'])

        isKey = verify_key(bytes.fromhex(rd["key"]),
                           os.path.join(rd['filePath'], "MSG", "MicroMsg.db")) if rd['key'] != "None" and rd[
            'filePath'] != "None" else False
        if rd['filePath'] != "None" and rd['key'] == "None" and not isKey:
            rd['key'] = get_key(rd['pid'], rd['filePath'], addrLen)
    except Exception as e:
        error = f"[-] WeChat Get Info Error:{e}"
        if is_logging: print(error)
    return rd


# 读取微信信息(account,mobile,name,mail,wxid,key)
def read_info(version_list: dict = None, is_logging: bool = False, save_path: str = None):
    """
    读取微信信息(account,mobile,name,mail,wxid,key)
    :param version_list:  版本偏移量
    :param is_logging:  是否打印日志
    :param save_path:  保存路径
    :return: 返回微信信息 [{"pid": pid, "version": version, "account": account,
                          "mobile": mobile, "name": name, "mail": mail, "wxid": wxid,
                          "key": key, "filePath": filePath}, ...]
    """
    if version_list is None:
        version_list = {}

    wechat_process = []
    result = []
    error = ""
    for process in psutil.process_iter(['name', 'exe', 'pid', 'cmdline']):
        if process.name() == 'WeChat.exe':
            wechat_process.append(process)

    if len(wechat_process) <= 0:
        error = "[-] WeChat No Run"
        if is_logging: print(error)
        return error

    for process in wechat_process:
        rd = get_details(process, version_list, is_logging)
        result.append(rd)

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

    if save_path:
        try:
            infos = json.load(open(save_path, "r", encoding="utf-8")) if os.path.exists(save_path) else []
        except:
            infos = []
        with open(save_path, "w", encoding="utf-8") as f:
            infos += result
            json.dump(infos, f, ensure_ascii=False, indent=4)
    return result


def get_wechat_db(require_list: Union[List[str], str] = "all", msg_dir: str = None, wxid: Union[List[str], str] = None,
                  is_logging: bool = False, is_return_list: bool = False) -> Union[str, dict, list]:
    r"""
    获取微信数据库路径
    :param require_list:  需要获取的数据库类型
    :param msg_dir:  微信数据库目录 eg: C:\Users\user\Documents\WeChat Files
    :param wxid:  微信id
    :param is_logging:  是否打印日志
    :return:
    """

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
            pattern[require] = re.compile(r"%s.*?\.db$" % require)
    else:
        error = f"[-] 参数错误: {require_list}"
        if is_logging: print(error)
        return error

    if is_return_list:  # 如果返回列表,返回值：{wxid:[db_path1,db_path2]}
        db_list = {}
        # 获取数据库路径
        for user, user_dir in user_dirs.items():  # 遍历用户目录
            db_list[user] = []
            for root, dirs, files in os.walk(user_dir):
                for file_name in files:
                    for n, p in pattern.items():
                        if p.match(file_name):
                            src_path = os.path.join(root, file_name)
                            db_list[user].append(src_path)
        return db_list

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


def get_core_db(wx_path: str, db_type: list = None) -> [str]:
    """
    获取聊天消息核心数据库路径
    :param wx_path: 微信文件夹路径 eg：C:\*****\WeChat Files\wxid*******
    :param db_type: 数据库类型 eg: ["MSG", "MediaMSG", "MicroMsg"]，三个中选择一个或多个
    :return: 返回数据库路径 eg:["",""]
    """
    if not os.path.exists(wx_path):
        return False, f"[-] 目录不存在: {wx_path}"
    db_type_all = ["MSG", "MediaMSG", "MicroMsg", "OpenIMContact", "OpenIMMedia", "OpenIMMsg", "Favorite"]

    if not db_type:
        db_type = db_type_all

    db_type = [dt for dt in db_type if dt in db_type_all]

    msg_dir = os.path.dirname(wx_path)
    my_wxid = os.path.basename(wx_path)
    WxDbPath = get_wechat_db(db_type, msg_dir, wxid=my_wxid, is_logging=False, is_return_list=True)  # 获取微信数据库路径
    if isinstance(WxDbPath, str):  # 如果返回的是字符串，则表示出错
        return False, WxDbPath
    wxdbpaths = WxDbPath.get(wx_path, [])
    if len(wxdbpaths) == 0:
        return False, "未获取到数据库路径"
    return True, wxdbpaths


if __name__ == '__main__':
    from pywxdump import VERSION_LIST

    read_info(VERSION_LIST, is_logging=True)
