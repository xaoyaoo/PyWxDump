# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         get_wx_db.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/14
# -------------------------------------------------------------------------------
import os
import re
import winreg
from typing import List, Union


def get_wechat_db(require_list: Union[List[str], str] = "all", msg_dir: str = None, wxid: Union[List[str], str] = None,
                  is_logging: bool = False):
    if not msg_dir:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat", 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "FileSavePath")
            winreg.CloseKey(key)
            w_dir = value
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
                else:
                    w_dir = documents_path
            except Exception as e:
                profile = os.path.expanduser("~")
                w_dir = os.path.join(profile, "Documents")
        msg_dir = os.path.join(w_dir, "WeChat Files")

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
    require_list = ["MediaMSG", "MicroMsg", "FTSMSG", "MSG", "Sns", "Emotion"]
    # require_list = "all"
    user_dirs = get_wechat_db(require_list, is_logging=True)
