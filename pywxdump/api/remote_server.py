# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         remote_server.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/01/02
# -------------------------------------------------------------------------------
import datetime
import json
import os
import time
import shutil
from collections import Counter
from urllib.parse import quote, unquote
from typing import List, Optional

import fastapi.requests
from pydantic import BaseModel
from fastapi import APIRouter, Response, Body, Query, Request
from starlette.responses import StreamingResponse, FileResponse

import pywxdump
from pywxdump import decrypt_merge, get_core_db
from pywxdump.db import DBHandler
from pywxdump.db.utils import download_file, dat2img
from .api_utils.html import HtmlController

from .export import export_csv, export_json, export_html
from .export.exportJSON import export_json_mini, export_json_mini_time_limit
from .rjson import ReJson, RqJson
from .utils import error9999, gc, asyncError9999, rs_loger

rs_api = APIRouter()


# 是否初始化
@rs_api.api_route('/is_init', methods=["GET", 'POST'])
@error9999
def is_init():
    """
    是否初始化
    :return:
    """

    local_wxids = gc.get_local_wxids()
    if len(local_wxids) > 1:
        return ReJson(0, True)
    return ReJson(0, False)


# start 以下为聊天联系人相关api *******************************************************************************************

@rs_api.api_route('/mywxid', methods=["GET", 'POST'])
@error9999
def mywxid():
    """
    获取我的微信id
    :return:
    """
    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    return ReJson(0, {"my_wxid": my_wxid})


@rs_api.api_route('/user_session_list', methods=["GET", 'POST'])
@error9999
def user_session_list():
    """
    获取联系人列表
    :return:
    """
    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_conf(my_wxid, "db_config")
    db = DBHandler(db_config, my_wxid=my_wxid)
    ret = db.get_session_list()
    return ReJson(0, list(ret.values()))


@rs_api.api_route('/user_labels_dict', methods=["GET", 'POST'])
@error9999
def user_labels_dict():
    """
    获取标签字典
    :return:
    """

    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_conf(my_wxid, "db_config")
    db = DBHandler(db_config, my_wxid=my_wxid)
    user_labels_dict = db.get_labels()
    return ReJson(0, user_labels_dict)


@rs_api.post('/user_list')
@error9999
def user_list(word: str = Body("", embed=True), wxids: List[str] = Body(None), labels: List[str] = Body(None)):
    """
    获取联系人列表，可用于搜索
    :return:
    """
    if isinstance(wxids, str) and wxids == '' or wxids is None: wxids = []
    if isinstance(labels, str) and labels == '' or labels is None: labels = []

    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_conf(my_wxid, "db_config")
    db = DBHandler(db_config, my_wxid=my_wxid)
    users = db.get_user(word=word, wxids=wxids, labels=labels)
    return ReJson(0, users)


# end 以上为聊天联系人相关api *********************************************************************************************

# start 以下为聊天记录相关api *********************************************************************************************

@rs_api.post('/msg_count')
@error9999
def msg_count(wxids: Optional[List[str]] = Body(..., embed=True)):
    """
    获取联系人的聊天记录数量
    :return:
    """
    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_db_config()
    db = DBHandler(db_config, my_wxid=my_wxid)
    count = db.get_msgs_count(wxids)
    return ReJson(0, count)


@rs_api.api_route('/msg_list', methods=["GET", 'POST'])
@error9999
def get_msgs(wxid: str = Body(...), start: int = Body(...), limit: int = Body(...)):
    """
    获取联系人的聊天记录
    :return:
    """

    my_wxid = gc.get_conf(gc.at, "last")

    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_conf(my_wxid, "db_config")

    db = DBHandler(db_config, my_wxid=my_wxid)

    start_createtime = datetime.datetime.strptime("2025-04-28 00:54:33",
                                                  "%Y-%m-%d %H:%M:%S").timestamp()
    end_createtime = datetime.datetime.now().timestamp()
    msgs, users = db.get_msgs(wxids=wxid, start_index=start, page_size=limit, )  #

    return ReJson(0, {"msg_list": msgs, "user_list": users})


@rs_api.get('/imgsrc')
@asyncError9999
async def get_imgsrc(request: Request):
    """
    获取图片,
    1. 从网络获取图片，主要功能只是下载图片，缓存到本地
    2. 读取本地图片
    :return:
    """
    imgsrc = unquote(str(request.query_params).replace("src=", "", 1))
    if not imgsrc:
        return ReJson(1002)
    if imgsrc.startswith("FileStorage"):  # 如果是本地图片文件则调用get_img
        my_wxid = gc.get_conf(gc.at, "last")
        if not my_wxid: return ReJson(1001, body="my_wxid is required")
        wx_path = gc.get_conf(my_wxid, "wx_path")

        img_path = imgsrc.replace("\\\\", "\\")

        img_tmp_path = os.path.join(gc.work_path, my_wxid, "img")
        original_img_path = os.path.join(wx_path, img_path)
        if os.path.exists(original_img_path):
            rc, fomt, md5, out_bytes = dat2img(original_img_path)
            if not rc:
                return ReJson(1001, body=original_img_path)
            imgsavepath = os.path.join(str(img_tmp_path), img_path + "_" + "".join([md5, fomt]))
            if os.path.exists(imgsavepath):
                return FileResponse(imgsavepath)
            if not os.path.exists(os.path.dirname(imgsavepath)):
                os.makedirs(os.path.dirname(imgsavepath))
            with open(imgsavepath, "wb") as f:
                f.write(out_bytes)
            return Response(content=out_bytes, media_type="image/jpeg")
        else:
            return ReJson(1001, body=f"{original_img_path} not exists")
    elif imgsrc.startswith("http://") or imgsrc.startswith("https://"):
        # 将?后面的参数连接到imgsrc

        my_wxid = gc.get_conf(gc.at, "last")
        if not my_wxid: return ReJson(1001, body="my_wxid is required")

        img_tmp_path = os.path.join(gc.work_path, my_wxid, "imgsrc")
        if not os.path.exists(img_tmp_path):
            os.makedirs(img_tmp_path)
        file_name = imgsrc.replace("http://", "").replace("https://", "").replace("/", "_").replace("?", "_")
        file_name = file_name + ".jpg"
        # 如果文件名过长，则将文件明分为目录和文件名
        if len(file_name) > 255:
            file_name = file_name[:255] + "/" + file_name[255:]

        img_path_all = os.path.join(str(img_tmp_path), file_name)
        if os.path.exists(img_path_all):
            return FileResponse(img_path_all)
        else:
            # proxies = {
            #     "http": "http://127.0.0.1:10809",
            #     "https": "http://127.0.0.1:10809",
            # }
            proxies = None
            download_file(imgsrc, img_path_all, proxies=proxies)
            if os.path.exists(img_path_all):
                return FileResponse(img_path_all)
            else:
                return ReJson(4004, body=imgsrc)
    else:
        return ReJson(1002, body=imgsrc)


@rs_api.api_route('/video', methods=["GET", 'POST'])
def get_video(request: Request):
    """
    获取视频
    :return:
    """
    videoPath = unquote(str(request.query_params).replace("src=", "", 1))
    if not videoPath:
        return ReJson(1002)
    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    wx_path = gc.get_conf(my_wxid, "wx_path")

    videoPath = videoPath.replace("\\\\", "\\")

    video_tmp_path = os.path.join(gc.work_path, my_wxid, "video")
    original_img_path = os.path.join(wx_path, videoPath)
    if not os.path.exists(original_img_path):
        return ReJson(5002)
    # 复制文件到临时文件夹
    assert isinstance(video_tmp_path, str)
    video_save_path = os.path.join(video_tmp_path, videoPath)
    if not os.path.exists(os.path.dirname(video_save_path)):
        os.makedirs(os.path.dirname(video_save_path))
    if os.path.exists(video_save_path):
        return FileResponse(path=video_save_path)
    shutil.copy(original_img_path, video_save_path)
    return FileResponse(path=video_save_path)


@rs_api.api_route('/audio', methods=["GET", 'POST'])
def get_audio(request: Request):
    """
    获取语音
    :return:
    """
    savePath = unquote(str(request.query_params).replace("src=", "", 1)).replace("audio\\", "", 1)
    if not savePath:
        return ReJson(1002)
    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_conf(my_wxid, "db_config")

    savePath = os.path.join(gc.work_path, my_wxid, "audio", savePath)  # 这个是从url中获取的
    if os.path.exists(savePath):
        assert isinstance(savePath, str)
        return FileResponse(path=savePath, media_type='audio/mpeg')

    MsgSvrID = savePath.split("_")[-1].replace(".wav", "")
    if not savePath:
        return ReJson(1002)

    # 判断savePath路径的文件夹是否存在
    if not os.path.exists(os.path.dirname(savePath)):
        os.makedirs(os.path.dirname(savePath))

    db = DBHandler(db_config, my_wxid=my_wxid)
    wave_data = db.get_audio(MsgSvrID, is_play=False, is_wave=True, save_path=savePath, rate=24000)
    if not wave_data:
        return ReJson(1001, body="wave_data is required")

    if os.path.exists(savePath):
        assert isinstance(savePath, str)
        return FileResponse(path=savePath, media_type='audio/mpeg')
    else:
        return ReJson(4004, body=savePath)


@rs_api.api_route('/file_info', methods=["GET", 'POST'])
def get_file_info(file_path: str = Body(..., embed=True)):
    if not file_path:
        return ReJson(1002)

    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    wx_path = gc.get_conf(my_wxid, "wx_path")

    all_file_path = os.path.join(wx_path, file_path)
    if not os.path.exists(all_file_path):
        return ReJson(5002)
    file_name = os.path.basename(all_file_path)
    file_size = os.path.getsize(all_file_path)
    return ReJson(0, {"file_name": file_name, "file_size": str(file_size)})


@rs_api.get('/file')
def get_file(request: Request):
    """
    获取文件
    :return:
    """
    file_path = unquote(str(request.query_params).replace("src=", "", 1))
    if not file_path:
        return ReJson(1002)
    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    wx_path = gc.get_conf(my_wxid, "wx_path")

    all_file_path = os.path.join(wx_path, file_path)
    if not os.path.exists(all_file_path):
        return ReJson(5002)

    def file_iterator(file_path, chunk_size=8192):
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    headers = {
        "Content-Disposition": f'attachment; filename*=UTF-8\'\'{quote(os.path.basename(all_file_path))}',
    }
    return StreamingResponse(file_iterator(all_file_path), media_type="application/octet-stream", headers=headers)


# end 以上为聊天记录相关api *********************************************************************************************

# start 导出聊天记录 *****************************************************************************************************
class ExportEndbRequest(BaseModel):
    wx_path: str = ""
    outpath: str = ""
    key: str = ""


@rs_api.api_route('/export_endb', methods=["GET", 'POST'])
def get_export_endb(request: ExportEndbRequest):
    """
    导出加密数据库
    :return:
    """

    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")

    wx_path = request.wx_path
    if not wx_path:
        wx_path = gc.get_conf(my_wxid, "wx_path")
    if not os.path.exists(wx_path if wx_path else ""):
        return ReJson(1002, body=f"wx_path is required: {wx_path}")

    # 分割wx_path的文件名和父目录
    code, wxdbpaths = get_core_db(wx_path)
    if not code:
        return ReJson(2001, body=wxdbpaths)

    outpath = os.path.join(gc.work_path, "export", my_wxid, "endb")
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    for wxdb in wxdbpaths:
        # 复制wxdb->outpath, os.path.basename(wxdb)
        assert isinstance(outpath, str)  # 为了解决pycharm的警告, 无实际意义
        wxdb_path = wxdb.get("db_path")
        shutil.copy(wxdb_path, os.path.join(outpath, os.path.basename(wxdb_path)))
    return ReJson(0, body=outpath)


class ExportDedbRequest(BaseModel):
    wx_path: str = ""
    outpath: str = ""
    key: str = ""


@rs_api.api_route('/export_dedb', methods=["GET", "POST"])
def get_export_dedb(request: ExportDedbRequest):
    """
    导出解密数据库
    :return:
    """
    key = request.key
    wx_path = request.wx_path

    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")

    if not key:
        key = gc.get_conf(my_wxid, "key")
    if not wx_path:
        wx_path = gc.get_conf(my_wxid, "wx_path")

    if not key:
        return ReJson(1002, body=f"key is required: {key}")
    if not wx_path:
        return ReJson(1002, body=f"wx_path is required: {wx_path}")
    if not os.path.exists(wx_path):
        return ReJson(1001, body=f"wx_path not exists: {wx_path}")

    outpath = os.path.join(gc.work_path, "export", my_wxid, "dedb")
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    assert isinstance(outpath, str)
    code, merge_save_path = decrypt_merge(wx_path=wx_path, key=key, outpath=outpath)
    time.sleep(1)
    if code:
        return ReJson(0, body=merge_save_path)
    else:
        return ReJson(2001, body=merge_save_path)


@rs_api.api_route('/export_csv', methods=["GET", 'POST'])
def get_export_csv(wxid: str = Body(..., embed=True)):
    """
    导出csv
    :return:
    """
    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_conf(my_wxid, "db_config")

    # st_ed_time = request.json.get("datetime", [0, 0])
    if not wxid:
        return ReJson(1002, body=f"username is required: {wxid}")
    # if not isinstance(st_ed_time, list) or len(st_ed_time) != 2:
    #     return ReJson(1002, body=f"datetime is required: {st_ed_time}")
    # start, end = st_ed_time
    # if not isinstance(start, int) or not isinstance(end, int) or start >= end:
    #     return ReJson(1002, body=f"datetime is required: {st_ed_time}")

    outpath = os.path.join(gc.work_path, "export", my_wxid, "csv", wxid)
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    code, ret = export_csv(wxid, outpath, db_config, my_wxid=my_wxid)
    if code:
        return ReJson(0, ret)
    else:
        return ReJson(2001, body=ret)


@rs_api.api_route('/export_json', methods=["GET", 'POST'])
def get_export_json(wxid: str = Body(..., embed=True)):
    """
    导出json
    :return:
    """
    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_conf(my_wxid, "db_config")

    if not wxid:
        return ReJson(1002, body=f"username is required: {wxid}")

    outpath = os.path.join(gc.work_path, "export", my_wxid, "json", wxid)
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    code, ret = export_json(wxid, outpath, db_config, my_wxid=my_wxid)
    if code:
        return ReJson(0, ret)
    else:
        return ReJson(2001, body=ret)


class ExportJsonMiniRequest(BaseModel):
    start_createtime: int
    end_createtime: int


@rs_api.api_route('/export_json_mini_select_time', methods=["GET", 'POST'])
def get_export_json(wxid: str = Body(..., embed=True), time: ExportJsonMiniRequest = Body(..., embed=True)):
    """
    导出json,选择时间，迷你版本
    :return:
    """

    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_conf(my_wxid, "db_config")

    if not wxid:
        return ReJson(1002, body=f"username is required: {wxid}")

    outpath = os.path.join(gc.work_path, "export", my_wxid, "json", wxid)
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    start_createtime = time.start_createtime / 1000.0  # 格式为 时间戳
    end_createtime = time.end_createtime  / 1000.0


    start_createtime = datetime.datetime.fromtimestamp(float(start_createtime)).strftime("%Y-%m-%d %H:%M:%S")  #转换成日期格式
    end_createtime = datetime.datetime.fromtimestamp(float(end_createtime)).strftime("%Y-%m-%d %H:%M:%S")

    code, ret, filename = export_json_mini_time_limit(wxid, outpath, db_config, my_wxid=my_wxid,
                                                      start_createtime=start_createtime, end_createtime=end_createtime)
    if code:
        # 成功创建，执行生成可视化页面的逻辑
        # with open(os.path.join(gc.work_path, "export", my_wxid, "html", wxid, filename), "w", encoding="utf-8") as f:
        #     f.write(
        #         #现在是fake
        #         HtmlController().create_html(json_data=None)
        #     )
        return ReJson(0, ret)

    else:
        return ReJson(2001, body=ret)


class ExportHtmlRequest(BaseModel):
    wxid: str


@rs_api.api_route('/export_html', methods=["GET", 'POST'])
def get_export_html(wxid: str = Body(..., embed=True)):
    """
    导出json
    :return:
    """
    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_conf(my_wxid, "db_config")

    if not wxid:
        return ReJson(1002, body=f"username is required: {wxid}")

    html_outpath = os.path.join(gc.work_path, "export", my_wxid, "html")
    if not os.path.exists(html_outpath):
        os.makedirs(html_outpath)
    assert isinstance(html_outpath, str)
    outpath = os.path.join(html_outpath, wxid)
    if os.path.exists(outpath):
        shutil.rmtree(outpath, ignore_errors=True)
    # 复制pywxdump/ui/web/*到outpath
    web_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "web")
    shutil.copytree(web_path, outpath)

    code, ret = export_html(wxid, outpath, db_config, my_wxid=my_wxid)

    if code:
        return ReJson(0, ret)
    else:
        return ReJson(2001, body=ret)


# end 导出聊天记录 *******************************************************************************************************


# AI可视化生成 **********************************************
#TODO:查询当前登录用户文件夹下是否有导出数据，是否已经存在ui界面

def recursive_listdir(path,list:List):
    """
    遍历文件夹获取所有文件 包括子目录
    """

    files = os.listdir(path)
    for file in files:
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            recursive_listdir(file_path,list)
        elif os.path.isfile(file_path):
            list.append(file_path)



def de_weight(l1:List,l2:List):
    """
    列表去重，针对特定对象
    """
    len1 = min(len(l1), len(l2))
    len1 = len1-1 if len1 > 0 else 0
    for i in range(len1):
        if l1[i]["wxid"] == l2[i]["wxid"] and l1[i]["start_time"] == l2[i]["start_time"] and l1[i]["end_time"] == l2[i][
            "end_time"]:
            l1[i]["flag"] = True
            l2.pop(i)

    return l1+l2






@rs_api.api_route('/ai_ui_json_list', methods=["GET", 'POST'])
def get_ai_ui_json_list():
    """
    获取可视化json文件列表
    """
    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")


    # 遍历json文件夹，查找最后带_ai的文件
    work_path = os.path.join(gc.work_path, "export", my_wxid, "json")
    if not os.path.exists(work_path):
        os.makedirs(work_path)
    file_list:List[str]=[]
    recursive_listdir(work_path,list=file_list)

    # 解析文件名
    ui_list = []
    for file in file_list:
        if file.split('.')[0].split('_')[-1] == 'ai':
            # 可进行ai可视化的文件
            ui_list.append(file)
    # print(ui_list)

    # 构造字典对象
    ui_dict_list = []
    for s in ui_list:
        wxid = s.split('\\')[-1].split('.')[0].split('_')[0] if "@" in s.split('\\')[-1] else \
        s.split('\\')[-1].split('.')[0].split('_')[1]  # wxid
        time_start = " ".join(s.split('\\')[-1].split('.')[0].split('_')[2:4]) if "@" in s.split('\\')[
            -1] else " ".join(s.split('\\')[-1].split('.')[0].split('_')[3:5])  # time start
        time_end = " ".join(s.split('\\')[-1].split('.')[0].split('_')[5:7]) if "@" in s.split('\\')[-1] else " ".join(
            s.split('\\')[-1].split('.')[0].split('_')[6:8])  # time end
        ui_dict_list.append({"wxid": wxid, "start_time": time_start, "end_time": time_end, "flag": False})



    # 遍历ai_json文件夹,获取所有文件名
    work_path = os.path.join(gc.work_path, "export", my_wxid, "ai_json")
    if not os.path.exists(work_path):
        os.makedirs(work_path)
    file_list:List[str]=[]
    recursive_listdir(work_path,list=file_list)

    # 解析文件名
    ai_list = []
    for file in file_list:
        ai_list.append(file)

    ai_dict_list = []

    # 构造字典对象
    for s in ai_list:
        wxid = s.split('\\')[-1].split('.')[0].split('_')[0] if "@" in s.split('\\')[-1] else \
        s.split('\\')[-1].split('.')[0].split('_')[1]  # wxid
        time_start = " ".join(s.split('\\')[-1].split('.')[0].split('_')[2:4]) if "@" in s.split('\\')[
            -1] else " ".join(s.split('\\')[-1].split('.')[0].split('_')[3:5])  # time start
        time_end = " ".join(s.split('\\')[-1].split('.')[0].split('_')[5:7]) if "@" in s.split('\\')[-1] else " ".join(
            s.split('\\')[-1].split('.')[0].split('_')[6:8])  # time end
        ai_dict_list.append({"wxid": wxid, "start_time": time_start, "end_time": time_end, "flag": True})

    # # 合并两个字典列表
    # dict_list = ui_dict_list + ai_dict_list
    # print(ui_dict_list)
    # print(ai_dict_list)

    # 去重
    dict_list = de_weight(ui_dict_list,ai_dict_list)

    return ReJson(0,body={"items":dict_list})




def get_file_path(work_path: str, file_name: str) -> str | None:
    """
    获取ai_json文件路径
    """
    # 遍历文件夹内的所有文件，找到对应文件名的文件路径


    path_list = os.listdir(work_path)
    for path in path_list:
        full_path = os.path.join(work_path, path)
        if os.path.isfile(full_path) and path == file_name:
            return full_path
        elif os.path.isdir(full_path):
            result = get_file_path(full_path, file_name)
            if result is not None:
                return result
    return None

class FileNameRequest(BaseModel):
    wxid: str
    start_time: str
    end_time: str

@rs_api.api_route('/db_to_ai_json', methods=["GET", 'POST'])
def db_to_ai_json(file_name: FileNameRequest = Body(..., embed=True)):
    """
    导出聊天记录到ai_json
    """
    start_time = file_name.start_time
    end_time = file_name.end_time
    wxid = file_name.wxid


    file_name = wxid + '_mini_' + start_time.replace(' ', '_').replace(':', '-') + '_to_' + end_time.replace(' ', '_').replace(':', '-') + '_ai'
    # file_name = wxid + '_aiyes_' + start_time.replace(' ', '_').replace(':', '-') + '_' + end_time.replace(' ', '_').replace(':', '-')
    file_name = file_name + '.json'



    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")



    result = get_file_path(os.path.join(gc.work_path, "export", my_wxid, "json"), file_name)


    if result is None:
        return ReJson(1002, body=f"file not found: {file_name}")

    # 获取文件内容
    with open(result, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        if not json_data:
            return ReJson(1002, body=f"json_data is empty: {file_name}")

    #通过llm处理，生成ai_json
    from .api_utils.llm import DeepSeekApi
    # 获取apikey
    apikey = gc.get_conf(my_wxid, "deepseek_setting").get("API_KEY")
    if not apikey:
        return ReJson(1002, body="deepseek_setting.API_KEY is required")
    llm_api = DeepSeekApi(api_key=apikey)
    json_data = llm_api.send_msg(module=0,message=json.dumps(json_data))

    # 保存到ai_json
    ai_json_path = os.path.join(gc.work_path, "export", my_wxid, "ai_json")
    if not os.path.exists(ai_json_path):
        os.makedirs(ai_json_path)

    assert isinstance(ai_json_path, str)
    file_name = wxid + '_aiyes_' + start_time.replace(' ', '_').replace(':', '-') + '_to_' + end_time.replace(' ',
                                                                                                           '_').replace(
        ':', '-')
    file_name = file_name + '.json'
    ai_json_file_path = os.path.join(ai_json_path, file_name)
    with open(ai_json_file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False)

    return ReJson(0, body=f"save to {ai_json_file_path}")



class FileNameGetUiRequest(BaseModel):
    wxid: str
    start_time: str
    end_time: str

# 获取可视化界面json文件
@rs_api.api_route('/get_ui_json', methods=["GET", 'POST'])
def get_ui_json(file_name: FileNameGetUiRequest = Body(..., embed=True)):
    """
    获取可视化界面json文件
    """
    # print(file_name.wxid)

    start_time = file_name.start_time
    end_time = file_name.end_time
    wxid = file_name.wxid if "@" in file_name.wxid else "wxid_" + file_name.wxid


    # start_time = datetime.datetime.fromtimestamp(float(start_time)).strftime("%Y-%m-%d %H:%M:%S")  #转换成日期格式
    # end_time = datetime.datetime.fromtimestamp(float(end_time)).strftime("%Y-%m-%d %H:%M:%S")

    file_name = wxid + '_aiyes_' + start_time.replace(' ', '_').replace(':', '-') + '_to_' + end_time.replace(' ', '_').replace(':', '-')
    file_name = file_name + '.json'


    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")

    result = get_file_path(os.path.join(gc.work_path, "export", my_wxid, "ai_json"), file_name)

    if result is None:
        return ReJson(1002, body=f"file not found: {file_name}")

    # 获取文件内容
    with open(result, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        if not json_data:
            return ReJson(1002, body=f"json_data is empty: {file_name}")

    return ReJson(0, body=json_data)






# AI可视化生成 *******************************************************************************************************



# start 聊天记录分析api **************************************************************************************************
class DateCountRequest(BaseModel):
    wxid: str = ""
    start_time: int = 0
    end_time: int = 0
    time_format: str = "%Y-%m-%d"


@rs_api.api_route('/date_count', methods=["GET", 'POST'])
def get_date_count(request: DateCountRequest):
    """
    获取日期统计
    :return:
    """
    wxid = request.wxid
    start_time = request.start_time
    end_time = request.end_time
    time_format = request.time_format

    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_conf(my_wxid, "db_config")
    db = DBHandler(db_config, my_wxid=my_wxid)
    date_count = db.get_date_count(wxid=wxid, start_time=start_time, end_time=end_time, time_format=time_format)
    return ReJson(0, date_count)


class TopTalkerCountRequest(BaseModel):
    top: int = 10
    start_time: int = 0
    end_time: int = 0


@rs_api.api_route('/top_talker_count', methods=["GET", 'POST'])
def get_top_talker_count(request: TopTalkerCountRequest):
    """
    获取最多聊天的人
    :return:
    """
    top = request.top
    start_time = request.start_time
    end_time = request.end_time

    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_conf(my_wxid, "db_config")
    date_count = DBHandler(db_config, my_wxid=my_wxid).get_top_talker_count(top=top, start_time=start_time,
                                                                            end_time=end_time)
    return ReJson(0, date_count)


class WordCloudRequest(BaseModel):
    target: str = "signature"


@rs_api.api_route('/wordcloud', methods=["GET", 'POST'])
@error9999
def get_wordcloud(request: WordCloudRequest):
    try:
        import jieba
    except ImportError:
        return ReJson(9999, body="jieba is required")

    target = request.target
    if not target:
        return ReJson(1002, body="target is required")

    my_wxid = gc.get_conf(gc.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = gc.get_conf(my_wxid, "db_config")
    db = DBHandler(db_config, my_wxid=my_wxid)

    if target == "signature":
        users = db.get_user()
        signature_list = []
        for wxid, user in users.items():
            ExtraBuf = user.get("ExtraBuf", {})
            signature = ExtraBuf.get("个性签名", "") if ExtraBuf else ""
            if signature:
                signature_list.append(signature)
        signature_str = " ".join(signature_list)
        words = jieba.lcut(signature_str)
        words = [word for word in words if len(word) > 1]
        count_dict = dict(Counter(words))
        return ReJson(0, count_dict)
    elif target == "nickname":
        users = db.get_user()
        nickname_list = []
        for wxid, user in users.items():
            nickname = user.get("nickname", "")
            if nickname:
                nickname_list.append(nickname)
        nickname_str = " ".join(nickname_list)
        words = jieba.lcut(nickname_str)
        words = [word for word in words if len(word) > 1]
        count_dict = dict(Counter(words))
        return ReJson(0, count_dict)

    return ReJson(1002, body="target is required")


# end 聊天记录分析api ****************************************************************************************************

# 关于、帮助、设置 *******************************************************************************************************
@rs_api.api_route('/check_update', methods=["GET", 'POST'])
@error9999
def check_update():
    """
    检查更新
    :return:
    """
    url = "https://api.github.com/repos/xaoyaoo/PyWxDump/tags"
    try:
        import requests
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            NEW_VERSION = data[0].get("name")
            if NEW_VERSION[1:] != pywxdump.__version__:
                msg = "有新版本"
            else:
                msg = "已经是最新版本"
            return ReJson(0, body={"msg": msg, "latest_version": NEW_VERSION,
                                   "latest_url": "https://github.com/xaoyaoo/PyWxDump/releases/tag/" + NEW_VERSION})
        else:
            return ReJson(2001, body="status_code is not 200")
    except Exception as e:
        return ReJson(9999, msg=str(e))


@rs_api.api_route('/version', methods=["GET", "POST"])
@error9999
def version():
    """
    版本
    :return:
    """
    return ReJson(0, pywxdump.__version__)


@rs_api.api_route('/get_readme', methods=["GET", 'POST'])
@error9999
def get_readme():
    """
    版本
    :return:
    """
    url = "https://raw.githubusercontent.com/xaoyaoo/PyWxDump/master/doc/README_CN.md"
    import requests
    res = requests.get(url)
    if res.status_code == 200:
        data = res.text
        data = data.replace("# <center>PyWxDump</center>", "")
        return ReJson(0, body=data)
    else:
        return ReJson(2001, body="status_code is not 200")


class DifyApiModel(BaseModel):
    api_key: str
    base_url: str


@rs_api.api_route('/dify_setting', methods=["GET", 'POST'])
@error9999
def dify_setting(request: Request = None, dify: DifyApiModel = Body(None, embed=True)):
    """
    dify设置
    """

    if request.method == "GET":
        my_wxid = gc.get_conf(gc.at, "last")
        if not my_wxid: return ReJson(1001, body="my_wxid is required")
        gc.get_conf(my_wxid, "dify_setting")

        return ReJson(0, body=gc.get_conf(my_wxid, "dify_setting"))

    elif request.method == "POST":
        my_wxid = gc.get_conf(gc.at, "last")
        if not my_wxid: return ReJson(1001, body="my_wxid is required")
        if not dify.api_key and not dify.base_url:
            return ReJson(1002, body="dify_setting is required")

        gc.set_conf(my_wxid, "dify_setting", {"API_KEY": dify.api_key, "BASE_URL": dify.base_url})
        return ReJson(0, body=gc.get_conf(my_wxid, "dify_setting"))
    return ReJson(2001, body="status_code is not 200")


class DeepSeekApiModel(BaseModel):
    api_key: str


@rs_api.api_route('/deepseek_setting', methods=["GET", 'POST'])
@error9999
def deepseek_setting(request: Request = None, deepseek: DeepSeekApiModel = Body(None, embed=True)):
    """
    deepseek设置
    """
    if request.method == "GET":
        my_wxid = gc.get_conf(gc.at, "last")
        if not my_wxid: return ReJson(1001, body="my_wxid is required")
        gc.get_conf(my_wxid, "deepseek_setting")

        return ReJson(0, body=gc.get_conf(my_wxid, "deepseek_setting"))

    elif request.method == "POST":
        my_wxid = gc.get_conf(gc.at, "last")
        if not my_wxid: return ReJson(1001, body="my_wxid is required")
        if not deepseek or not deepseek.api_key:
            return ReJson(1002, body="deepseek_setting is required")

        gc.set_conf(my_wxid, "deepseek_setting", {"API_KEY": deepseek.api_key})
        return ReJson(0, body=gc.get_conf(my_wxid, "deepseek_setting"))
    return ReJson(2001, body="status_code is not 200")

# END 关于、帮助、设置 ***************************************************************************************************
