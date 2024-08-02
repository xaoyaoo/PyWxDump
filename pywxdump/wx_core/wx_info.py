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
from typing import List, Union
from .utils import verify_key, get_exe_bit, wx_core_error
from .utils import get_process_list, get_memory_maps, get_process_exe_path, get_file_version_info
from .utils import search_memory
from .utils import wx_core_loger, DB_TYPE_CORE
import ctypes.wintypes as wintypes

# 定义常量
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
OpenProcess = kernel32.OpenProcess
OpenProcess.restype = wintypes.HANDLE
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]

CloseHandle = kernel32.CloseHandle
CloseHandle.restype = wintypes.BOOL
CloseHandle.argtypes = [wintypes.HANDLE]

ReadProcessMemory = kernel32.ReadProcessMemory
void_p = ctypes.c_void_p


# 读取内存中的字符串(key部分)
@wx_core_error
def get_key_by_offs(h_process, address, address_len=8):
    array = ctypes.create_string_buffer(address_len)
    if ReadProcessMemory(h_process, void_p(address), array, address_len, 0) == 0: return None
    address = int.from_bytes(array, byteorder='little')  # 逆序转换为int地址（key地址）
    key = ctypes.create_string_buffer(32)
    if ReadProcessMemory(h_process, void_p(address), key, 32, 0) == 0: return None
    key_string = bytes(key).hex()
    return key_string


# 读取内存中的字符串(非key部分)
@wx_core_error
def get_info_string(h_process, address, n_size=64):
    array = ctypes.create_string_buffer(n_size)
    if ReadProcessMemory(h_process, void_p(address), array, n_size, 0) == 0: return None
    array = bytes(array).split(b"\x00")[0] if b"\x00" in array else bytes(array)
    text = array.decode('utf-8', errors='ignore')
    return text.strip() if text.strip() != "" else None


# 读取内存中的字符串(昵称部分name)
@wx_core_error
def get_info_name(h_process, address, address_len=8, n_size=64):
    array = ctypes.create_string_buffer(n_size)
    if ReadProcessMemory(h_process, void_p(address), array, n_size, 0) == 0: return None
    address1 = int.from_bytes(array[:address_len], byteorder='little')  # 逆序转换为int地址（key地址）
    info_name = get_info_string(h_process, address1, n_size)
    if info_name != None:
        return info_name
    array = bytes(array).split(b"\x00")[0] if b"\x00" in array else bytes(array)
    text = array.decode('utf-8', errors='ignore')
    return text.strip() if text.strip() != "" else None


# 读取内存中的wxid
@wx_core_error
def get_info_wxid(h_process):
    find_num = 100
    addrs = search_memory(h_process, br'\\Msg\\FTSContact', max_num=find_num)
    wxids = []
    for addr in addrs:
        array = ctypes.create_string_buffer(80)
        if ReadProcessMemory(h_process, void_p(addr - 30), array, 80, 0) == 0: return None
        array = bytes(array)  # .split(b"\\")[0]
        array = array.split(b"\\Msg")[0]
        array = array.split(b"\\")[-1]
        wxids.append(array.decode('utf-8', errors='ignore'))
    wxid = max(wxids, key=wxids.count) if wxids else None
    return wxid


# 读取内存中的wx_path基于wxid（慢）
@wx_core_error
def get_wx_dir_by_wxid(h_process, wxid=""):
    find_num = 10
    addrs = search_memory(h_process, wxid.encode() + br'\\Msg\\FTSContact', max_num=find_num)
    wxid_dir = []
    for addr in addrs:
        win_addr_len = 260
        array = ctypes.create_string_buffer(win_addr_len)
        if ReadProcessMemory(h_process, void_p(addr - win_addr_len + 50), array, win_addr_len, 0) == 0: return None
        array = bytes(array).split(b"\\Msg")[0]
        array = array.split(b"\00")[-1]
        wxid_dir.append(array.decode('utf-8', errors='ignore'))
    wxid_dir = max(wxid_dir, key=wxid_dir.count) if wxid_dir else None
    return wxid_dir


@wx_core_error
def get_wx_dir_by_reg(wxid="all"):
    """
    # 读取 wx_dir (微信文件路径) （快）
    :param wxid: 微信id
    :return: 返回wx_dir,if wxid="all" return wx_dir else return wx_dir/wxid
    """
    if not wxid:
        return None
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

    wx_dir = os.path.join(w_dir, "WeChat Files")

    if wxid and wxid != "all":
        wxid_dir = os.path.join(wx_dir, wxid)
        return wxid_dir if os.path.exists(wxid_dir) else None
    return wx_dir if os.path.exists(wx_dir) else None


def get_wx_dir(wxid: str = "", Handle=None):
    """
    综合运用多种方法获取wx_path
    优先调用 get_wx_dir_by_reg (该方法速度快)
    次要调用 get_wx_dir_by_wxid （该方法通过搜索内存进行，速度较慢）
    """
    if wxid:
        wx_dir = get_wx_dir_by_reg(wxid) if wxid else None
        if wxid is not None and wx_dir is None and Handle:  # 通过wxid获取wx_path,如果wx_path为空则通过wxid获取wx_path
            wx_dir = get_wx_dir_by_wxid(Handle, wxid=wxid)
    else:
        wx_dir = get_wx_dir_by_reg()
    return wx_dir


@wx_core_error
def get_key_by_mem_search(pid, db_path, addr_len):
    """
    获取key （慢）
    :param pid: 进程id
    :param db_path: 微信数据库路径
    :param addr_len: 地址长度
    :return: 返回key
    """

    def read_key_bytes(h_process, address, address_len=8):
        array = ctypes.create_string_buffer(address_len)
        if ReadProcessMemory(h_process, void_p(address), array, address_len, 0) == 0: return None
        address = int.from_bytes(array, byteorder='little')  # 逆序转换为int地址（key地址）
        key = ctypes.create_string_buffer(32)
        if ReadProcessMemory(h_process, void_p(address), key, 32, 0) == 0: return None
        key_bytes = bytes(key)
        return key_bytes

    phone_type1 = "iphone\x00"
    phone_type2 = "android\x00"
    phone_type3 = "ipad\x00"

    MicroMsg_path = os.path.join(db_path, "MSG", "MicroMsg.db")

    start_adress = 0x7FFFFFFFFFFFFFFF
    end_adress = 0

    memory_maps = get_memory_maps(pid)
    for module in memory_maps:
        if module.FileName and 'WeChatWin.dll' in module.FileName:
            s = module.BaseAddress
            e = module.BaseAddress + module.RegionSize
            start_adress = s if s < start_adress else start_adress
            end_adress = e if e > end_adress else end_adress

    hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    type1_addrs = search_memory(hProcess, phone_type1.encode(), max_num=2, start_address=start_adress,
                                end_address=end_adress)
    type2_addrs = search_memory(hProcess, phone_type2.encode(), max_num=2, start_address=start_adress,
                                end_address=end_adress)
    type3_addrs = search_memory(hProcess, phone_type3.encode(), max_num=2, start_address=start_adress,
                                end_address=end_adress)

    type_addrs = []
    if len(type1_addrs) >= 2: type_addrs += type1_addrs
    if len(type2_addrs) >= 2: type_addrs += type2_addrs
    if len(type3_addrs) >= 2: type_addrs += type3_addrs
    if len(type_addrs) == 0: return None

    type_addrs.sort()  # 从小到大排序

    for i in type_addrs[::-1]:
        for j in range(i, i - 2000, -addr_len):
            key_bytes = read_key_bytes(hProcess, j, addr_len)
            if key_bytes == None:
                continue
            if verify_key(key_bytes, MicroMsg_path):
                return key_bytes.hex()
    CloseHandle(hProcess)
    return None


@wx_core_error
def get_wx_key(key: str = "", wx_dir: str = "", pid=0, addrLen=8):
    """
    获取key （慢）
    :param key: 微信key
    :param wx_dir: 微信文件路径
    :param pid: 进程id
    :param addrLen: 地址长度
    :return: 返回key
    """
    isKey = verify_key(
        bytes.fromhex(key),
        os.path.join(wx_dir, "MSG", "MicroMsg.db")) if key is not None and wx_dir is not None else False
    if wx_dir is not None and not isKey:
        key = get_key_by_mem_search(pid, wx_dir, addrLen)
    return key


@wx_core_error
def get_info_details(pid, WX_OFFS: dict = None):
    path = get_process_exe_path(pid)
    rd = {'pid': pid, 'version': get_file_version_info(path),
          "account": None, "mobile": None, "nickname": None, "mail": None,
          "wxid": None, "key": None, "wx_dir": None}
    try:
        bias_list = WX_OFFS.get(rd['version'], None)

        Handle = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)

        addrLen = get_exe_bit(path) // 8
        if not isinstance(bias_list, list) or len(bias_list) <= 4:
            wx_core_loger.warning(f"[-] WeChat Current Version Is Not Supported(not get account,mobile,nickname,mail)")
        else:
            wechat_base_address = 0
            memory_maps = get_memory_maps(pid)
            for module in memory_maps:
                if module.FileName and 'WeChatWin.dll' in module.FileName:
                    wechat_base_address = module.BaseAddress
                    rd['version'] = get_file_version_info(module.FileName) if os.path.exists(module.FileName) else rd[
                        'version']
                    bias_list = WX_OFFS.get(rd['version'], None)
                    break
            if wechat_base_address != 0:
                name_baseaddr = wechat_base_address + bias_list[0]
                account_baseaddr = wechat_base_address + bias_list[1]
                mobile_baseaddr = wechat_base_address + bias_list[2]
                mail_baseaddr = wechat_base_address + bias_list[3]
                key_baseaddr = wechat_base_address + bias_list[4]

                rd['account'] = get_info_string(Handle, account_baseaddr, 32) if bias_list[1] != 0 else None
                rd['mobile'] = get_info_string(Handle, mobile_baseaddr, 64) if bias_list[2] != 0 else None
                rd['nickname'] = get_info_name(Handle, name_baseaddr, addrLen, 64) if bias_list[0] != 0 else None
                rd['mail'] = get_info_string(Handle, mail_baseaddr, 64) if bias_list[3] != 0 else None
                rd['key'] = get_key_by_offs(Handle, key_baseaddr, addrLen) if bias_list[4] != 0 else None
            else:
                wx_core_loger.warning(f"[-] WeChat WeChatWin.dll Not Found")

        rd['wxid'] = get_info_wxid(Handle)
        rd['wx_dir'] = get_wx_dir(rd['wxid'], Handle)
        rd['key'] = get_wx_key(rd['key'], rd['wx_dir'], rd['pid'], addrLen)

        CloseHandle(Handle)
    except Exception as e:
        wx_core_loger.error(f"[-] WeChat Get Info Error:{e}", exc_info=True)
    return rd


# 读取微信信息(account,mobile,nickname,mail,wxid,key)
@wx_core_error
def get_wx_info(WX_OFFS: dict = None, is_print: bool = False, save_path: str = None):
    """
    读取微信信息(account,mobile,nickname,mail,wxid,key)
    :param WX_OFFS:  版本偏移量
    :param is_print:  是否打印结果
    :param save_path:  保存路径
    :return: 返回微信信息 [{"pid": pid, "version": version, "account": account,
                          "mobile": mobile, "nickname": nickname, "mail": mail, "wxid": wxid,
                          "key": key, "wx_dir": wx_dir}, ...]
    """
    if WX_OFFS is None:
        WX_OFFS = {}

    wechat_pids = []
    result = []

    processes = get_process_list()
    for pid, name in processes:
        if name == "WeChat.exe":
            wechat_pids.append(pid)

    if len(wechat_pids) <= 0:
        wx_core_loger.error("[-] WeChat No Run")
        return result

    for pid in wechat_pids:
        rd = get_info_details(pid, WX_OFFS)
        result.append(rd)

    if is_print:
        print("=" * 32)
        if isinstance(result, str):  # 输出报错
            print(result)
        else:  # 输出结果
            for i, rlt in enumerate(result):
                for k, v in rlt.items():
                    print(f"[+] {k:>8}: {v if v else 'None'}")
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


@wx_core_error
def get_wx_db(msg_dir: str = None,
              db_types: Union[List[str], str] = None,
              wxids: Union[List[str], str] = None) -> List[dict]:
    r"""
    获取微信数据库路径
    :param msg_dir:  微信数据库目录 eg: C:\Users\user\Documents\WeChat Files （非wxid目录）
    :param db_types:  需要获取的数据库类型,如果为空,则获取所有数据库
    :param wxids:  微信id列表,如果为空,则获取所有wxid下的数据库
    :return: [{"wxid": wxid, "db_type": db_type, "db_path": db_path, "wxid_dir": wxid_dir}, ...]
    """
    result = []

    if not msg_dir or not os.path.exists(msg_dir):
        wx_core_loger.warning(f"[-] 微信文件目录不存在: {msg_dir}, 将使用默认路径")
        msg_dir = get_wx_dir_by_reg(wxid="all")

    if not os.path.exists(msg_dir):
        wx_core_loger.error(f"[-] 目录不存在: {msg_dir}", exc_info=True)
        return result

    wxids = wxids.split(";") if isinstance(wxids, str) else wxids
    if not isinstance(wxids, list) or len(wxids) <= 0:
        wxids = None
    db_types = db_types.split(";") if isinstance(db_types, str) else db_types
    if not isinstance(db_types, list) or len(db_types) <= 0:
        db_types = None

    wxid_dirs = {}  # wx用户目录
    for sub_dir in os.listdir(msg_dir):
        if os.path.isdir(os.path.join(msg_dir, sub_dir)) and sub_dir not in ["All Users", "Applet", "WMPF"]:
            wxid_dirs[os.path.basename(sub_dir)] = os.path.join(msg_dir, sub_dir)

    for wxid, wxid_dir in wxid_dirs.items():
        if wxids and wxid not in wxids:  # 如果指定wxid,则过滤掉其他wxid
            continue
        for root, dirs, files in os.walk(wxid_dir):
            for file_name in files:
                if not file_name.endswith(".db"):
                    continue
                db_type = re.sub(r"\d*\.db$", "", file_name)
                if db_types and db_type not in db_types:  # 如果指定db_type,则过滤掉其他db_type
                    continue
                db_path = os.path.join(root, file_name)
                result.append({"wxid": wxid, "db_type": db_type, "db_path": db_path, "wxid_dir": wxid_dir})
    return result


@wx_core_error
def get_core_db(wx_path: str, db_types: list = None) -> [dict]:
    """
    获取聊天消息核心数据库路径
    :param wx_path: 微信文件夹路径 eg：C:\*****\WeChat Files\wxid*******
    :param db_types: 数据库类型 eg: DB_TYPE_CORE，中选择一个或多个
    :return: 返回数据库路径 eg: [{"wxid": wxid, "db_type": db_type, "db_path": db_path, "wxid_dir": wxid_dir}, ...]
    """
    if not os.path.exists(wx_path):
        return False, f"[-] 目录不存在: {wx_path}"

    if not db_types:
        db_types = DB_TYPE_CORE
    db_types = [dt for dt in db_types if dt in DB_TYPE_CORE]
    msg_dir = os.path.dirname(wx_path)
    my_wxid = os.path.basename(wx_path)
    wxdbpaths = get_wx_db(msg_dir=msg_dir, db_types=db_types, wxids=my_wxid)

    if len(wxdbpaths) == 0:
        wx_core_loger.error(f"[-] get_core_db 未获取到数据库路径")
        return False, "未获取到数据库路径"
    return True, wxdbpaths


if __name__ == '__main__':
    from pywxdump import WX_OFFS

    get_wx_info(WX_OFFS, is_print=True)
