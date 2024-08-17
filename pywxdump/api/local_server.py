# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         local_server.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/08/01
# -------------------------------------------------------------------------------
import os
import time
import shutil
import pythoncom

from pydantic import BaseModel
from fastapi import APIRouter, Body

from pywxdump import all_merge_real_time_db, get_wx_db
from pywxdump import get_wx_info, batch_decrypt, BiasAddr, merge_db, decrypt_merge

from .rjson import ReJson, RqJson
from .utils import error9999, ls_loger, random_str, gc

ls_api = APIRouter()


# 以下为初始化相关 *******************************************************************************************************

@ls_api.post('/init_last_local_wxid')
@error9999
def init_last_local_wxid():
    """
    初始化，包括key
    :return:
    """
    local_wxid = gc.get_local_wxids()
    local_wxid.remove(gc.at)
    if local_wxid:
        return ReJson(0, {"local_wxids": local_wxid})
    return ReJson(0, {"local_wxids": []})


@ls_api.post('/init_last')
@error9999
def init_last(my_wxid: str = Body(..., embed=True)):
    """
    是否初始化
    :return:
    """
    my_wxid = my_wxid.strip().strip("'").strip('"') if isinstance(my_wxid, str) else ""
    if not my_wxid:
        my_wxid = gc.get_conf(gc.at, "last")
        if not my_wxid: return ReJson(1001, body="my_wxid is required")
    if my_wxid:
        gc.set_conf(gc.at, "last", my_wxid)
        merge_path = gc.get_conf(my_wxid, "merge_path")
        wx_path = gc.get_conf(my_wxid, "wx_path")
        key = gc.get_conf(my_wxid, "key")
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


class InitKeyRequest(BaseModel):
    wx_path: str
    key: str
    my_wxid: str


@ls_api.post('/init_key')
@error9999
def init_key(request: InitKeyRequest):
    """
    初始化key
    :param request:
    :return:
    """
    wx_path = request.wx_path.strip().strip("'").strip('"')
    key = request.key.strip().strip("'").strip('"')
    my_wxid = request.my_wxid.strip().strip("'").strip('"')
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

    out_path = os.path.join(gc.work_path, "decrypted", my_wxid) if my_wxid else os.path.join(gc.work_path, "decrypted")
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
        if not os.path.exists(os.path.join(gc.work_path, my_wxid)):
            os.makedirs(os.path.join(gc.work_path, my_wxid))
        merge_save_path_new = os.path.join(gc.work_path, my_wxid, "merge_all.db")
        shutil.move(merge_save_path, str(merge_save_path_new))

        # 删除out_path
        if os.path.exists(out_path):
            try:
                shutil.rmtree(out_path)
            except PermissionError as e:
                # 显示堆栈信息
                ls_loger.error(f"{e}", exc_info=True)
        db_config = {
            "key": random_str(16),
            "type": "sqlite",
            "path": merge_save_path_new
        }
        gc.set_conf(my_wxid, "db_config", db_config)
        gc.set_conf(my_wxid, "db_config", db_config)
        gc.set_conf(my_wxid, "merge_path", merge_save_path_new)
        gc.set_conf(my_wxid, "wx_path", wx_path)
        gc.set_conf(my_wxid, "key", key)
        gc.set_conf(my_wxid, "my_wxid", my_wxid)
        gc.set_conf(gc.at, "last", my_wxid)
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


class InitNoKeyRequest(BaseModel):
    merge_path: str
    wx_path: str
    my_wxid: str


@ls_api.post('/init_nokey')
@error9999
def init_nokey(request: InitNoKeyRequest):
    """
    初始化，包括key
    :return:
    """
    merge_path = request.merge_path.strip().strip("'").strip('"')
    wx_path = request.wx_path.strip().strip("'").strip('"')
    my_wxid = request.my_wxid.strip().strip("'").strip('"')

    if not wx_path:
        return ReJson(1002, body=f"wx_path is required: {wx_path}")
    if not os.path.exists(wx_path):
        return ReJson(1001, body=f"wx_path not exists: {wx_path}")
    if not merge_path:
        return ReJson(1002, body=f"merge_path is required: {merge_path}")
    if not my_wxid:
        return ReJson(1002, body=f"my_wxid is required: {my_wxid}")

    key = gc.get_conf(my_wxid, "key")
    db_config = {
        "key": random_str(16),
        "type": "sqlite",
        "path": merge_path
    }
    gc.set_conf(my_wxid, "db_config", db_config)
    gc.set_conf(my_wxid, "merge_path", merge_path)
    gc.set_conf(my_wxid, "wx_path", wx_path)
    gc.set_conf(my_wxid, "key", key)
    gc.set_conf(my_wxid, "my_wxid", my_wxid)
    gc.set_conf(gc.at, "last", my_wxid)
    rdata = {
        "merge_path": merge_path,
        "wx_path": wx_path,
        "key": "",
        "my_wxid": my_wxid,
        "is_init": True,
    }
    return ReJson(0, rdata)


# END 以上为初始化相关 ***************************************************************************************************


@ls_api.api_route('/realtimemsg', methods=["GET", "POST"])
@error9999
def get_real_time_msg():
    """
    获取实时消息 使用 merge_real_time_db()函数
    :return:
    """
    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")

    merge_path = gc.get_conf(my_wxid, "merge_path")
    key = gc.get_conf(my_wxid, "key")
    wx_path = gc.get_conf(my_wxid, "wx_path")

    if not merge_path or not key or not wx_path or not wx_path:
        return ReJson(1002, body="msg_path or media_path or wx_path or key is required")

    real_time_exe_path = gc.get_conf(gc.at, "real_time_exe_path")

    code, ret = all_merge_real_time_db(key=key, wx_path=wx_path, merge_path=merge_path,
                                       real_time_exe_path=real_time_exe_path)
    if code:
        return ReJson(0, ret)
    else:
        return ReJson(2001, body=ret)


# start 这部分为专业工具的api *********************************************************************************************

@ls_api.api_route('/wxinfo', methods=["GET", 'POST'])
@error9999
def get_wxinfo():
    """
    获取微信信息
    :return:
    """
    import pythoncom
    from pywxdump import WX_OFFS
    pythoncom.CoInitialize()  # 初始化COM库
    wxinfos = get_wx_info(WX_OFFS)
    pythoncom.CoUninitialize()  # 释放COM库
    return ReJson(0, wxinfos)


class BiasAddrRequest(BaseModel):
    mobile: str
    name: str
    account: str
    key: str = ""
    wxdbPath: str = ""


@ls_api.post('/biasaddr')
@error9999
def get_biasaddr(request: BiasAddrRequest):
    """
    BiasAddr
    :return:
    """
    mobile = request.mobile
    name = request.name
    account = request.account
    key = request.json.key
    wxdbPath = request.wxdbPath
    if not mobile or not name or not account:
        return ReJson(1002)
    pythoncom.CoInitialize()
    rdata = BiasAddr(account, mobile, name, key, wxdbPath).run()
    return ReJson(0, str(rdata))


@ls_api.api_route('/decrypt', methods=["GET", 'POST'])
@error9999
def get_decrypt(key: str, wxdbPath: str, outPath: str = ""):
    """
    解密
    :return:
    """
    if not outPath:
        outPath = gc.work_path
    wxinfos = batch_decrypt(key, wxdbPath, out_path=outPath)
    return ReJson(0, str(wxinfos))


class MergeRequest(BaseModel):
    dbPath: str
    outPath: str


@ls_api.post('/merge')
@error9999
def get_merge(request: MergeRequest):
    """
    合并
    :return:
    """
    wxdb_path = request.dbPath
    out_path = request.outPath
    db_path = get_wx_db(wxdb_path)
    # for i in db_path:print(i)
    rdata = merge_db(db_path, out_path)
    return ReJson(0, str(rdata))

# END 这部分为专业工具的api ***********************************************************************************************
