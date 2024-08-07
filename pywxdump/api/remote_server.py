# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         chat_api.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/01/02
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
from pywxdump import get_core_db, all_merge_real_time_db
from pywxdump.api.rjson import ReJson, RqJson
from pywxdump.api.utils import get_conf, get_conf_wxids, set_conf, error9999, gen_base64, validate_title, \
    get_conf_local_wxid
from pywxdump import get_wx_info, WX_OFFS, batch_decrypt, BiasAddr, merge_db, decrypt_merge, merge_real_time_db

from pywxdump.db import DBHandler, download_file, export_csv, export_json, dat2img

# app = Flask(__name__, static_folder='../ui/web/dist', static_url_path='/')

rs_api = Blueprint('rs_api', __name__, template_folder='../ui/web', static_folder='../ui/web/assets/', )
rs_api.debug = False


# 是否初始化
@rs_api.route('/api/rs/is_init', methods=["GET", 'POST'])
@error9999
def is_init():
    """
    是否初始化
    :return:
    """
    local_wxids = get_conf_local_wxid(g.caf)
    if len(local_wxids) > 1:
        return ReJson(0, True)
    return ReJson(0, False)


# start 以下为聊天联系人相关api *******************************************************************************************

@rs_api.route('/api/rs/mywxid', methods=["GET", 'POST'])
@error9999
def mywxid():
    """
    获取我的微信id
    :return:
    """
    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    return ReJson(0, {"my_wxid": my_wxid})


@rs_api.route('/api/rs/user_session_list', methods=["GET", 'POST'])
@error9999
def user_session_list():
    """
    获取联系人列表
    :return:
    """
    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = get_conf(g.caf, my_wxid, "db_config")
    db = DBHandler(db_config)
    ret = db.get_session_list()
    return ReJson(0, list(ret.values()))


@rs_api.route('/api/rs/user_labels_dict', methods=["GET", 'POST'])
@error9999
def user_labels_dict():
    """
    获取标签字典
    :return:
    """
    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = get_conf(g.caf, my_wxid, "db_config")
    db = DBHandler(db_config)
    user_labels_dict = db.get_labels()
    return ReJson(0, user_labels_dict)


@rs_api.route('/api/rs/user_list', methods=["GET", 'POST'])
@error9999
def user_list():
    """
    获取联系人列表，可用于搜索
    :return:
    """
    if request.method == "GET":
        word = request.args.get("word", "")
        wxids = request.args.get("wxids", [])
        labels = request.args.get("labels", [])
    elif request.method == "POST":
        word = request.json.get("word", "")
        wxids = request.json.get("wxids", [])
        labels = request.json.get("labels", [])
    else:
        return ReJson(1003, msg="Unsupported method")

    if isinstance(wxids, str) and wxids == '' or wxids is None: wxids = []
    if isinstance(labels, str) and labels == '' or labels is None: labels = []

    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = get_conf(g.caf, my_wxid, "db_config")
    db = DBHandler(db_config)
    users = db.get_user(word, wxids, labels)
    return ReJson(0, users)


# end 以上为聊天联系人相关api *********************************************************************************************

# start 以下为聊天记录相关api *********************************************************************************************


@rs_api.route('/api/rs/imgsrc/<path:imgsrc>', methods=["GET", 'POST'])
@error9999
def get_imgsrc(imgsrc):
    """
    获取图片,
    1. 从网络获取图片，主要功能只是下载图片，缓存到本地
    2. 读取本地图片
    :return:
    """
    if not imgsrc:
        return ReJson(1002)
    if imgsrc.startswith("FileStorage"):  # 如果是本地图片文件则调用get_img
        my_wxid = get_conf(g.caf, g.at, "last")
        if not my_wxid: return ReJson(1001, body="my_wxid is required")
        wx_path = get_conf(g.caf, my_wxid, "wx_path")

        img_path = imgsrc.replace("\\\\", "\\")

        img_tmp_path = os.path.join(g.work_path, my_wxid, "img")
        original_img_path = os.path.join(wx_path, img_path)
        if os.path.exists(original_img_path):
            rc, fomt, md5, out_bytes = dat2img(original_img_path)
            if not rc:
                return ReJson(1001, body=original_img_path)
            imgsavepath = os.path.join(str(img_tmp_path), img_path + "_" + "".join([md5, fomt]))
            if os.path.exists(imgsavepath):
                return send_file(imgsavepath)
            if not os.path.exists(os.path.dirname(imgsavepath)):
                os.makedirs(os.path.dirname(imgsavepath))
            with open(imgsavepath, "wb") as f:
                f.write(out_bytes)
            return send_file(imgsavepath)
        else:
            return ReJson(1001, body=f"{original_img_path} not exists")
    elif imgsrc.startswith("http://") or imgsrc.startswith("https://"):
        # 将?后面的参数连接到imgsrc
        imgsrc = imgsrc + "?" + request.query_string.decode("utf-8") if request.query_string else imgsrc
        my_wxid = get_conf(g.caf, g.at, "last")
        if not my_wxid: return ReJson(1001, body="my_wxid is required")

        img_tmp_path = os.path.join(g.work_path, my_wxid, "imgsrc")
        if not os.path.exists(img_tmp_path):
            os.makedirs(img_tmp_path)
        file_name = imgsrc.replace("http://", "").replace("https://", "").replace("/", "_").replace("?", "_")
        file_name = file_name + ".jpg"
        # 如果文件名过长，则将文件明分为目录和文件名
        if len(file_name) > 255:
            file_name = file_name[:255] + "/" + file_name[255:]

        img_path_all = os.path.join(str(img_tmp_path), file_name)
        if os.path.exists(img_path_all):
            return send_file(img_path_all)
        else:
            download_file(imgsrc, img_path_all)
            if os.path.exists(img_path_all):
                return send_file(img_path_all)
            else:
                return ReJson(4004, body=imgsrc)
    else:
        return ReJson(1002, body=imgsrc)


@rs_api.route('/api/rs/msg_count', methods=["GET", 'POST'])
@error9999
def msg_count():
    """
    获取联系人的聊天记录数量
    :return:
    """
    if request.method == "GET":
        wxid = request.args.get("wxids", [])
    elif request.method == "POST":
        wxid = request.json.get("wxids", [])
    else:
        return ReJson(1003, msg="Unsupported method")

    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = get_conf(g.caf, my_wxid, "db_config")
    db = DBHandler(db_config)
    chat_count = db.get_msg_count(wxid)
    chat_count1 = db.get_plc_msg_count(wxid) if db.PublicMsg_exist else {}
    # 合并两个字典，相同key，则将value相加
    count = {k: chat_count.get(k, 0) + chat_count1.get(k, 0) for k in
             list(set(list(chat_count.keys()) + list(chat_count1.keys())))}
    return ReJson(0, count)


@rs_api.route('/api/rs/msg_list', methods=["GET", 'POST'])
@error9999
def get_msgs():
    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = get_conf(g.caf, my_wxid, "db_config")

    start = request.json.get("start")
    limit = request.json.get("limit")
    wxid = request.json.get("wxid")

    if not wxid:
        return ReJson(1002, body=f"wxid is required: {wxid}")
    if start and isinstance(start, str) and start.isdigit():
        start = int(start)
    if limit and isinstance(limit, str) and limit.isdigit():
        limit = int(limit)
    if start is None or limit is None:
        return ReJson(1002, body=f"start or limit is required {start} {limit}")
    if not isinstance(start, int) and not isinstance(limit, int):
        return ReJson(1002, body=f"start or limit is not int {start} {limit}")

    db = DBHandler(db_config)
    msgs, wxid_list = db.get_msg_list(wxid=wxid, start_index=start, page_size=limit)
    if not msgs and db.PublicMsg_exist:
        msgs, wxid_list = db.get_plc_msg_list(wxid=wxid, start_index=start, page_size=limit)
    wxid_list.append(my_wxid)
    user = db.get_user_list(wxids=wxid_list)
    return ReJson(0, {"msg_list": msgs, "user_list": user})


@rs_api.route('/api/rs/video/<path:videoPath>', methods=["GET", 'POST'])
def get_video(videoPath):
    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    wx_path = get_conf(g.caf, my_wxid, "wx_path")

    videoPath = videoPath.replace("\\\\", "\\")

    video_tmp_path = os.path.join(g.work_path, my_wxid, "video")
    original_img_path = os.path.join(wx_path, videoPath)
    if not os.path.exists(original_img_path):
        return ReJson(5002)
    # 复制文件到临时文件夹
    video_save_path = os.path.join(video_tmp_path, videoPath)
    if not os.path.exists(os.path.dirname(video_save_path)):
        os.makedirs(os.path.dirname(video_save_path))
    if os.path.exists(video_save_path):
        return send_file(video_save_path)
    shutil.copy(original_img_path, video_save_path)
    return send_file(original_img_path)


@rs_api.route('/api/rs/audio/<path:savePath>', methods=["GET", 'POST'])
def get_audio(savePath):
    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = get_conf(g.caf, my_wxid, "db_config")

    savePath = os.path.join(g.work_path, my_wxid, "audio", savePath)  # 这个是从url中获取的
    if os.path.exists(savePath):
        return send_file(savePath)

    MsgSvrID = savePath.split("_")[-1].replace(".wav", "")
    if not savePath:
        return ReJson(1002)

    # 判断savePath路径的文件夹是否存在
    if not os.path.exists(os.path.dirname(savePath)):
        os.makedirs(os.path.dirname(savePath))

    db = DBHandler(db_config)
    wave_data = db.get_audio(MsgSvrID, is_play=False, is_wave=True, save_path=savePath, rate=24000)
    if not wave_data:
        return ReJson(1001, body="wave_data is required")

    if os.path.exists(savePath):
        return send_file(savePath)
    else:
        return ReJson(4004, body=savePath)


@rs_api.route('/api/rs/file_info', methods=["GET", 'POST'])
def get_file_info():
    file_path = request.args.get("file_path")
    file_path = request.json.get("file_path", file_path)
    if not file_path:
        return ReJson(1002)

    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    wx_path = get_conf(g.caf, my_wxid, "wx_path")

    all_file_path = os.path.join(wx_path, file_path)
    if not os.path.exists(all_file_path):
        return ReJson(5002)
    file_name = os.path.basename(all_file_path)
    file_size = os.path.getsize(all_file_path)
    return ReJson(0, {"file_name": file_name, "file_size": str(file_size)})


@rs_api.route('/api/rs/file/<path:filePath>', methods=["GET", 'POST'])
def get_file(filePath):
    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    wx_path = get_conf(g.caf, my_wxid, "wx_path")

    all_file_path = os.path.join(wx_path, filePath)
    if not os.path.exists(all_file_path):
        return ReJson(5002)
    return send_file(all_file_path)


# end 以上为聊天记录相关api *********************************************************************************************

# start 导出聊天记录 *****************************************************************************************************

@rs_api.route('/api/rs/export_endb', methods=["GET", 'POST'])
def get_export_endb():
    """
    导出加密数据库
    :return:
    """
    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    wx_path = get_conf(g.caf, my_wxid, "wx_path")
    wx_path = request.json.get("wx_path", wx_path)

    if not wx_path:
        return ReJson(1002, body=f"wx_path is required: {wx_path}")
    if not os.path.exists(wx_path):
        return ReJson(1001, body=f"wx_path not exists: {wx_path}")

    # 分割wx_path的文件名和父目录
    code, wxdbpaths = get_core_db(wx_path)
    if not code:
        return ReJson(2001, body=wxdbpaths)

    outpath = os.path.join(g.work_path, "export", my_wxid, "endb")
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    for wxdb in wxdbpaths:
        # 复制wxdb->outpath, os.path.basename(wxdb)
        assert isinstance(outpath, str)  # 为了解决pycharm的警告, 无实际意义
        shutil.copy(wxdb, os.path.join(outpath, os.path.basename(wxdb)))
    return ReJson(0, body=outpath)


@rs_api.route('/api/rs/export_dedb', methods=["GET", "POST"])
def get_export_dedb():
    """
    导出解密数据库
    :return:
    """
    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")

    key = request.json.get("key", get_conf(g.caf, my_wxid, "key"))
    wx_path = request.json.get("wx_path", get_conf(g.caf, my_wxid, "wx_path"))

    if not key:
        return ReJson(1002, body=f"key is required: {key}")
    if not wx_path:
        return ReJson(1002, body=f"wx_path is required: {wx_path}")
    if not os.path.exists(wx_path):
        return ReJson(1001, body=f"wx_path not exists: {wx_path}")

    outpath = os.path.join(g.work_path, "export", my_wxid, "dedb")
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    code, merge_save_path = decrypt_merge(wx_path=wx_path, key=key, outpath=outpath)
    time.sleep(1)
    if code:
        return ReJson(0, body=merge_save_path)
    else:
        return ReJson(2001, body=merge_save_path)


@rs_api.route('/api/rs/export_csv', methods=["GET", 'POST'])
def get_export_csv():
    """
    导出csv
    :return:
    """
    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = get_conf(g.caf, my_wxid, "db_config")

    wxid = request.json.get("wxid")
    # st_ed_time = request.json.get("datetime", [0, 0])
    if not wxid:
        return ReJson(1002, body=f"username is required: {wxid}")
    # if not isinstance(st_ed_time, list) or len(st_ed_time) != 2:
    #     return ReJson(1002, body=f"datetime is required: {st_ed_time}")
    # start, end = st_ed_time
    # if not isinstance(start, int) or not isinstance(end, int) or start >= end:
    #     return ReJson(1002, body=f"datetime is required: {st_ed_time}")

    outpath = os.path.join(g.work_path, "export", my_wxid, "csv", wxid)
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    code, ret = export_csv(wxid, outpath, db_config)
    if code:
        return ReJson(0, ret)
    else:
        return ReJson(2001, body=ret)


@rs_api.route('/api/rs/export_json', methods=["GET", 'POST'])
def get_export_json():
    """
    导出json
    :return:
    """
    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = get_conf(g.caf, my_wxid, "db_config")

    wxid = request.json.get("wxid")
    if not wxid:
        return ReJson(1002, body=f"username is required: {wxid}")

    outpath = os.path.join(g.work_path, "export", my_wxid, "json", wxid)
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    code, ret = export_json(wxid, outpath, db_config)
    if code:
        return ReJson(0, ret)
    else:
        return ReJson(2001, body=ret)


# end 导出聊天记录 *******************************************************************************************************

# start 聊天记录分析api **************************************************************************************************

@rs_api.route('/api/rs/date_count', methods=["GET", 'POST'])
def get_date_count():
    """
    获取日期统计
    :return:
    """
    if request.method not in ["GET", "POST"]:
        return ReJson(1003, msg="Unsupported method")
    rq_data = request.json if request.method == "POST" else request.args
    word = rq_data.get("wxid", "")
    start_time = rq_data.get("start_time", 0)
    end_time = rq_data.get("end_time", 0)
    time_format = rq_data.get("time_format", "%Y-%m-%d")

    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = get_conf(g.caf, my_wxid, "db_config")
    db = DBHandler(db_config)
    date_count = db.get_date_count(wxid=word, start_time=start_time, end_time=end_time, time_format=time_format)
    return ReJson(0, date_count)


@rs_api.route('/api/rs/top_talker_count', methods=["GET", 'POST'])
def get_top_talker_count():
    """
    获取最多聊天的人
    :return:
    """
    if request.method not in ["GET", "POST"]:
        return ReJson(1003, msg="Unsupported method")
    rq_data = request.json if request.method == "POST" else request.args
    top = rq_data.get("top", 10)
    start_time = rq_data.get("start_time", 0)
    end_time = rq_data.get("end_time", 0)

    my_wxid = get_conf(g.caf, g.at, "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    db_config = get_conf(g.caf, my_wxid, "db_config")
    date_count = DBHandler(db_config).get_top_talker_count(top=top, start_time=start_time, end_time=end_time)
    return ReJson(0, date_count)


@rs_api.route('/api/rs/wordcloud', methods=["GET", 'POST'])
@error9999
def wordcloud():
    pass


# end 聊天记录分析api ****************************************************************************************************

# 关于、帮助、设置 *******************************************************************************************************
@rs_api.route('/api/rs/check_update', methods=["GET", 'POST'])
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


@rs_api.route('/api/rs/version', methods=["GET", 'POST'])
@error9999
def version():
    """
    版本
    :return:
    """
    return ReJson(0, pywxdump.__version__)


@rs_api.route('/api/rs/get_readme', methods=["GET", 'POST'])
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


# END 关于、帮助、设置 ***************************************************************************************************


@rs_api.route('/')
@error9999
def index():
    return render_template('index.html')
