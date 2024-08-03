# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         local_server.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/08/01
# -------------------------------------------------------------------------------
import base64
import json
import logging
import os
import re
import time
import shutil
import pythoncom
import pywxdump

from flask import Flask, request, render_template, g, Blueprint, send_file, make_response, session
from pywxdump import get_core_db, all_merge_real_time_db, get_wx_db
from pywxdump.api.rjson import ReJson, RqJson
from pywxdump.api.utils import get_conf, get_conf_wxids, set_conf, error9999, gen_base64, validate_title, \
    get_conf_local_wxid, ls_loger
from pywxdump import get_wx_info, WX_OFFS, batch_decrypt, BiasAddr, merge_db, decrypt_merge, merge_real_time_db

from pywxdump.db import DBHandler, download_file, export_csv, export_json

ls_api = Blueprint('ls_api', __name__, template_folder='../ui/web', static_folder='../ui/web/assets/', )
ls_api.debug = False


# 以下为初始化相关 *******************************************************************************************************

@ls_api.route('/api/ls/init_last_local_wxid', methods=["GET", 'POST'])
@error9999
def init_last_local_wxid():
    """
    初始化，包括key
    :return:
    """
    local_wxid = get_conf_local_wxid(g.caf)
    local_wxid.remove(g.at)
    if local_wxid:
        return ReJson(0, {"local_wxids": local_wxid})
    return ReJson(0, {"local_wxids": []})


@ls_api.route('/api/ls/init_last', methods=["GET", 'POST'])
@error9999
def init_last():
    """
    是否初始化
    :return:
    """
    my_wxid = request.json.get("my_wxid", "")
    my_wxid = my_wxid.strip().strip("'").strip('"') if isinstance(my_wxid, str) else ""
    if not my_wxid:
        my_wxid = get_conf(g.caf, "auto_setting", "last")
    if my_wxid:
        set_conf(g.caf, "auto_setting", "last", my_wxid)
        merge_path = get_conf(g.caf, my_wxid, "merge_path")
        wx_path = get_conf(g.caf, my_wxid, "wx_path")
        key = get_conf(g.caf, my_wxid, "key")
        rdata = {
            "merge_path": merge_path,
            "wx_path": wx_path,
            "key": key,
            "my_wxid": my_wxid,
            "is_init": True,
        }
        if merge_path and wx_path:
            return ReJson(0, rdata)
    return ReJson(0, {"is_init": False, "my_wxid": ""})


@ls_api.route('/api/ls/init_key', methods=["GET", 'POST'])
@error9999
def init_key():
    """
    初始化，包括key
    :return:
    """
    wx_path = request.json.get("wx_path", "").strip().strip("'").strip('"')
    key = request.json.get("key", "").strip().strip("'").strip('"')
    my_wxid = request.json.get("my_wxid", "").strip().strip("'").strip('"')
    if not wx_path:
        return ReJson(1002, body=f"wx_path is required: {wx_path}")
    if not os.path.exists(wx_path):
        return ReJson(1001, body=f"wx_path not exists: {wx_path}")
    if not key:
        return ReJson(1002, body=f"key is required: {key}")
    if not my_wxid:
        return ReJson(1002, body=f"my_wxid is required: {my_wxid}")

    # db_config = get_conf(g.caf, my_wxid, "db_config")
    # if isinstance(db_config, dict) and db_config and os.path.exists(db_config.get("path")):
    #     pmsg = DBHandler(db_config)
    #     # pmsg.close_all_connection()

    out_path = os.path.join(g.work_path, "decrypted", my_wxid) if my_wxid else os.path.join(g.work_path, "decrypted")
    # 检查文件夹中文件是否被占用
    if os.path.exists(out_path):
        try:
            shutil.rmtree(out_path)
        except PermissionError as e:
            # 显示堆栈信息
            ls_loger.error(f"{e}", exc_info=True)
            return ReJson(2001, body=str(e))

    code, merge_save_path = decrypt_merge(wx_path=wx_path, key=key, outpath=str(out_path))
    time.sleep(1)
    if code:
        # 移动merge_save_path到g.work_path/my_wxid
        if not os.path.exists(os.path.join(g.work_path, my_wxid)):
            os.makedirs(os.path.join(g.work_path, my_wxid))
        merge_save_path_new = os.path.join(g.work_path, my_wxid, "merge_all.db")
        shutil.move(merge_save_path, str(merge_save_path_new))

        # 删除out_path
        if os.path.exists(out_path):
            try:
                shutil.rmtree(out_path)
            except PermissionError as e:
                # 显示堆栈信息
                ls_loger.error(f"{e}", exc_info=True)
        db_config = {
            "key": "merge_all",
            "type": "sqlite",
            "path": merge_save_path_new
        }
        set_conf(g.caf, my_wxid, "db_config", db_config)
        set_conf(g.caf, my_wxid, "merge_path", merge_save_path_new)
        set_conf(g.caf, my_wxid, "wx_path", wx_path)
        set_conf(g.caf, my_wxid, "key", key)
        set_conf(g.caf, my_wxid, "my_wxid", my_wxid)
        set_conf(g.caf, "auto_setting", "last", my_wxid)
        rdata = {
            "merge_path": merge_save_path_new,
            "wx_path": wx_path,
            "key": key,
            "my_wxid": my_wxid,
            "is_init": True,
        }
        return ReJson(0, rdata)
    else:
        return ReJson(2001, body=merge_save_path)


@ls_api.route('/api/ls/init_nokey', methods=["GET", 'POST'])
@error9999
def init_nokey():
    """
    初始化，包括key
    :return:
    """
    merge_path = request.json.get("merge_path", "").strip().strip("'").strip('"')
    wx_path = request.json.get("wx_path", "").strip().strip("'").strip('"')
    my_wxid = request.json.get("my_wxid", "").strip().strip("'").strip('"')

    if not wx_path:
        return ReJson(1002, body=f"wx_path is required: {wx_path}")
    if not os.path.exists(wx_path):
        return ReJson(1001, body=f"wx_path not exists: {wx_path}")
    if not merge_path:
        return ReJson(1002, body=f"merge_path is required: {merge_path}")
    if not my_wxid:
        return ReJson(1002, body=f"my_wxid is required: {my_wxid}")

    key = get_conf(g.caf, my_wxid, "key")

    set_conf(g.caf, my_wxid, "merge_path", merge_path)
    set_conf(g.caf, my_wxid, "wx_path", wx_path)
    set_conf(g.caf, my_wxid, "key", key)
    set_conf(g.caf, my_wxid, "my_wxid", my_wxid)
    set_conf(g.caf, "test", "last", my_wxid)
    rdata = {
        "merge_path": merge_path,
        "wx_path": wx_path,
        "key": "",
        "my_wxid": my_wxid,
        "is_init": True,
    }
    return ReJson(0, rdata)


# END 以上为初始化相关 ***************************************************************************************************


@ls_api.route('/api/ls/realtimemsg', methods=["GET", "POST"])
@error9999
def get_real_time_msg():
    """
    获取实时消息 使用 merge_real_time_db()函数
    :return:
    """
    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")

    merge_path = get_conf(g.caf, my_wxid, "merge_path")
    key = get_conf(g.caf, my_wxid, "key")
    wx_path = get_conf(g.caf, my_wxid, "wx_path")

    if not merge_path or not key or not wx_path or not wx_path:
        return ReJson(1002, body="msg_path or media_path or wx_path or key is required")

    code, ret = all_merge_real_time_db(key=key, wx_path=wx_path, merge_path=merge_path)
    if code:
        return ReJson(0, ret)
    else:
        return ReJson(2001, body=ret)


# start 这部分为专业工具的api *********************************************************************************************

@ls_api.route('/api/ls/wxinfo', methods=["GET", 'POST'])
@error9999
def get_wxinfo():
    """
    获取微信信息
    :return:
    """
    import pythoncom
    pythoncom.CoInitialize()
    wxinfos = get_wx_info(WX_OFFS)
    pythoncom.CoUninitialize()
    return ReJson(0, wxinfos)


@ls_api.route('/api/ls/biasaddr', methods=["GET", 'POST'])
@error9999
def biasaddr():
    """
    BiasAddr
    :return:
    """
    mobile = request.json.get("mobile")
    name = request.json.get("name")
    account = request.json.get("account")
    key = request.json.get("key", "")
    wxdbPath = request.json.get("wxdbPath", "")
    if not mobile or not name or not account:
        return ReJson(1002)
    pythoncom.CoInitialize()
    rdata = BiasAddr(account, mobile, name, key, wxdbPath).run()
    return ReJson(0, str(rdata))


@ls_api.route('/api/ls/decrypt', methods=["GET", 'POST'])
@error9999
def decrypt():
    """
    解密
    :return:
    """
    key = request.json.get("key")
    if not key:
        return ReJson(1002)
    wxdb_path = request.json.get("wxdbPath")
    if not wxdb_path:
        return ReJson(1002)
    out_path = request.json.get("outPath")
    if not out_path:
        out_path = g.tmp_path
    wxinfos = batch_decrypt(key, wxdb_path, out_path=out_path)
    return ReJson(0, str(wxinfos))


@ls_api.route('/api/ls/merge', methods=["GET", 'POST'])
@error9999
def merge():
    """
    合并
    :return:
    """
    wxdb_path = request.json.get("dbPath")
    if not wxdb_path:
        return ReJson(1002)
    out_path = request.json.get("outPath")
    if not out_path:
        return ReJson(1002)
    db_path = get_wx_db(wxdb_path)
    # for i in db_path:print(i)
    rdata = merge_db(db_path, out_path)
    return ReJson(0, str(rdata))

# END 这部分为专业工具的api ***********************************************************************************************
