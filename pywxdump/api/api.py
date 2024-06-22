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
from pywxdump.api.utils import read_session, get_session_wxids, save_session, error9999, gen_base64, validate_title, \
    read_session_local_wxid
from pywxdump import read_info, VERSION_LIST, batch_decrypt, BiasAddr, merge_db, decrypt_merge, merge_real_time_db

from pywxdump.dbpreprocess import wxid2userinfo, ParsingMSG, get_user_list, get_recent_user_list, ParsingMediaMSG, \
    download_file, export_csv, export_json, ParsingMicroMsg
from pywxdump.dbpreprocess.utils import dat2img

# app = Flask(__name__, static_folder='../ui/web/dist', static_url_path='/')

api = Blueprint('api', __name__, template_folder='../ui/web', static_folder='../ui/web/assets/', )
api.debug = False


# 以下为初始化相关 *******************************************************************************************************
@api.route('/api/init_last_local_wxid', methods=["GET", 'POST'])
@error9999
def init_last_local_wxid():
    """
    初始化，包括key
    :return:
    """
    local_wxid = read_session_local_wxid(g.sf)
    if local_wxid:
        return ReJson(0, {"local_wxids": local_wxid})
    return ReJson(0, {"local_wxids": []})


@api.route('/api/init_last', methods=["GET", 'POST'])
@error9999
def init_last():
    """
    是否初始化
    :return:
    """
    my_wxid = request.json.get("my_wxid", "")
    my_wxid = my_wxid.strip().strip("'").strip('"') if isinstance(my_wxid, str) else ""
    if not my_wxid:
        my_wxid = read_session(g.sf, "test", "last")
    if my_wxid:
        save_session(g.sf, "test", "last", my_wxid)
        merge_path = read_session(g.sf, my_wxid, "merge_path")
        wx_path = read_session(g.sf, my_wxid, "wx_path")
        key = read_session(g.sf, my_wxid, "key")
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


@api.route('/api/init_key', methods=["GET", 'POST'])
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

    old_merge_save_path = read_session(g.sf, my_wxid, "merge_path")
    if isinstance(old_merge_save_path, str) and old_merge_save_path and os.path.exists(old_merge_save_path):
        pmsg = ParsingMSG(old_merge_save_path)
        pmsg.close_all_connection()

    out_path = os.path.join(g.tmp_path, "decrypted", my_wxid) if my_wxid else os.path.join(g.tmp_path, "decrypted")
    # 检查文件夹中文件是否被占用
    if os.path.exists(out_path):
        try:
            shutil.rmtree(out_path)
        except PermissionError as e:
            # 显示堆栈信息
            logging.error(f"{e}", exc_info=True)
            return ReJson(2001, body=str(e))

    code, merge_save_path = decrypt_merge(wx_path=wx_path, key=key, outpath=out_path)
    time.sleep(1)
    if code:
        # 移动merge_save_path到g.tmp_path/my_wxid
        if not os.path.exists(os.path.join(g.tmp_path, my_wxid)):
            os.makedirs(os.path.join(g.tmp_path, my_wxid))
        merge_save_path_new = os.path.join(g.tmp_path, my_wxid, "merge_all.db")
        shutil.move(merge_save_path, str(merge_save_path_new))

        # 删除out_path
        if os.path.exists(out_path):
            try:
                shutil.rmtree(out_path)
            except PermissionError as e:
                # 显示堆栈信息
                logging.error(f"{e}", exc_info=True)

        save_session(g.sf, my_wxid, "merge_path", merge_save_path_new)
        save_session(g.sf, my_wxid, "wx_path", wx_path)
        save_session(g.sf, my_wxid, "key", key)
        save_session(g.sf, my_wxid, "my_wxid", my_wxid)
        save_session(g.sf, "test", "last", my_wxid)
        rdata = {
            "merge_path": merge_save_path,
            "wx_path": wx_path,
            "key": key,
            "my_wxid": my_wxid,
            "is_init": True,
        }
        return ReJson(0, rdata)
    else:
        return ReJson(2001, body=merge_save_path)


@api.route('/api/init_nokey', methods=["GET", 'POST'])
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

    key = read_session(g.sf, my_wxid, "key")

    save_session(g.sf, my_wxid, "merge_path", merge_path)
    save_session(g.sf, my_wxid, "wx_path", wx_path)
    save_session(g.sf, my_wxid, "key", key)
    save_session(g.sf, my_wxid, "my_wxid", my_wxid)
    save_session(g.sf, "test", "last", my_wxid)
    rdata = {
        "merge_path": merge_path,
        "wx_path": wx_path,
        "key": "",
        "my_wxid": my_wxid,
        "is_init": True,
    }
    return ReJson(0, rdata)


# END 以上为初始化相关 ***************************************************************************************************


# start 以下为聊天联系人相关api *******************************************************************************************

@api.route('/api/recent_user_list', methods=["GET", 'POST'])
@error9999
def recent_user_list():
    """
    获取联系人列表
    :return:
    """
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    merge_path = read_session(g.sf, my_wxid, "merge_path")
    user_list = get_recent_user_list(merge_path, merge_path, limit=200)
    return ReJson(0, user_list)


@api.route('/api/user_labels_dict', methods=["GET", 'POST'])
@error9999
def user_labels_dict():
    """
    获取标签字典
    :return:
    """
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    merge_path = read_session(g.sf, my_wxid, "merge_path")
    user_labels_dict = ParsingMicroMsg(merge_path).labels_dict()
    return ReJson(0, user_labels_dict)


@api.route('/api/user_list', methods=["GET", 'POST'])
@error9999
def user_list():
    """
    获取联系人列表
    :return:
    """
    if request.method == "GET":
        word = request.args.get("word", "")
    elif request.method == "POST":
        word = request.json.get("word", "")
    else:
        return ReJson(1003, msg="Unsupported method")
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    merge_path = read_session(g.sf, my_wxid, "merge_path")
    user_list = get_user_list(merge_path, merge_path, word)
    return ReJson(0, user_list)


@api.route('/api/wxid2user', methods=["GET", 'POST'])
@error9999
def wxid2user():
    """
    获取联系人列表
    :return:
    """
    if request.method == "GET":
        word = request.args.get("wxid", "")
    elif request.method == "POST":
        word = request.json.get("wxid", "")
    else:
        return ReJson(1003, msg="Unsupported method")

    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    merge_path = read_session(g.sf, my_wxid, "merge_path")
    user_info = wxid2userinfo(merge_path, merge_path, wxid=word)
    return ReJson(0, user_info)


@api.route('/api/mywxid', methods=["GET", 'POST'])
@error9999
def mywxid():
    """
    获取我的微信id
    :return:
    """
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    return ReJson(0, {"my_wxid": my_wxid})


# end 以上为聊天联系人相关api *********************************************************************************************

# start 以下为聊天记录相关api *********************************************************************************************

@api.route('/api/realtimemsg', methods=["GET", "POST"])
@error9999
def get_real_time_msg():
    """
    获取实时消息 使用 merge_real_time_db()函数
    :return:
    """
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")

    merge_path = read_session(g.sf, my_wxid, "merge_path")
    key = read_session(g.sf, my_wxid, "key")
    wx_path = read_session(g.sf, my_wxid, "wx_path")

    if not merge_path or not key or not wx_path or not wx_path:
        return ReJson(1002, body="msg_path or media_path or wx_path or key is required")

    code, ret = all_merge_real_time_db(key=key, wx_path=wx_path, merge_path=merge_path)
    if code:
        return ReJson(0, ret)
    else:
        return ReJson(2001, body=ret)


@api.route('/api/msg_count', methods=["GET", 'POST'])
@error9999
def msg_count():
    """
    获取联系人的聊天记录数量
    :return:
    """
    if request.method == "GET":
        wxid = request.args.get("wxid")
    elif request.method == "POST":
        wxid = request.json.get("wxid")
    else:
        return ReJson(1003, msg="Unsupported method")

    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    merge_path = read_session(g.sf, my_wxid, "merge_path")
    chat_count = ParsingMSG(merge_path).msg_count(wxid)
    return ReJson(0, chat_count)


@api.route('/api/imgsrc/<path:imgsrc>', methods=["GET", 'POST'])
def get_imgsrc(imgsrc):
    """
    获取图片,从网络获取图片，主要功能只是下载图片，缓存到本地
    :return:
    """
    if not imgsrc:
        return ReJson(1002)

    if imgsrc.startswith("FileStorage"):  # 如果是本地图片文件则调用get_img
        return get_img(imgsrc)

    # 将?后面的参数连接到imgsrc
    imgsrc = imgsrc + "?" + request.query_string.decode("utf-8") if request.query_string else imgsrc

    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")

    img_tmp_path = os.path.join(g.tmp_path, my_wxid, "imgsrc")
    if not os.path.exists(img_tmp_path):
        os.makedirs(img_tmp_path)
    file_name = imgsrc.replace("http://", "").replace("https://", "").replace("/", "_").replace("?", "_")
    file_name = file_name + ".jpg"
    # 如果文件名过长，则将文件明分为目录和文件名
    if len(file_name) > 255:
        file_name = file_name[:255] + "/" + file_name[255:]

    img_path_all = os.path.join(img_tmp_path, file_name)
    if os.path.exists(img_path_all):
        return send_file(img_path_all)
    else:
        download_file(imgsrc, img_path_all)
        if os.path.exists(img_path_all):
            return send_file(img_path_all)
        else:
            return ReJson(4004, body=imgsrc)


@api.route('/api/img/<path:img_path>', methods=["GET", 'POST'])
@error9999
def get_img(img_path):
    """
    获取图片
    :return:
    """

    if not img_path:
        return ReJson(1002)

    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    wx_path = read_session(g.sf, my_wxid, "wx_path")

    img_path = img_path.replace("\\\\", "\\")

    img_tmp_path = os.path.join(g.tmp_path, my_wxid, "img")
    original_img_path = os.path.join(wx_path, img_path)
    if os.path.exists(original_img_path):
        fomt, md5, out_bytes = dat2img(original_img_path)
        imgsavepath = os.path.join(img_tmp_path, img_path + "_" + ".".join([md5, fomt]))
        if not os.path.exists(os.path.dirname(imgsavepath)):
            os.makedirs(os.path.dirname(imgsavepath))
        with open(imgsavepath, "wb") as f:
            f.write(out_bytes)
        return send_file(imgsavepath)
    else:
        return ReJson(1001, body=original_img_path)


@api.route('/api/msgs', methods=["GET", 'POST'])
@error9999
def get_msgs():
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    merge_path = read_session(g.sf, my_wxid, "merge_path")

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

    parsing_msg = ParsingMSG(merge_path)
    msgs, wxid_list = parsing_msg.msg_list(wxid, start, limit)
    wxid_list.append(my_wxid)
    user_list = wxid2userinfo(merge_path, merge_path, wxid_list)
    return ReJson(0, {"msg_list": msgs, "user_list": user_list})


@api.route('/api/video/<path:videoPath>', methods=["GET", 'POST'])
def get_video(videoPath):
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    wx_path = read_session(g.sf, my_wxid, "wx_path")

    videoPath = videoPath.replace("\\\\", "\\")

    video_tmp_path = os.path.join(g.tmp_path, my_wxid, "video")
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


@api.route('/api/audio/<path:savePath>', methods=["GET", 'POST'])
def get_audio(savePath):
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    merge_path = read_session(g.sf, my_wxid, "merge_path")

    savePath = os.path.join(g.tmp_path, my_wxid, "audio", savePath)  # 这个是从url中获取的
    if os.path.exists(savePath):
        return send_file(savePath)

    MsgSvrID = savePath.split("_")[-1].replace(".wav", "")
    if not savePath:
        return ReJson(1002)

    # 判断savePath路径的文件夹是否存在
    if not os.path.exists(os.path.dirname(savePath)):
        os.makedirs(os.path.dirname(savePath))

    parsing_media_msg = ParsingMediaMSG(merge_path)
    wave_data = parsing_media_msg.get_audio(MsgSvrID, is_play=False, is_wave=True, save_path=savePath, rate=24000)
    if not wave_data:
        return ReJson(1001, body="wave_data is required")

    if os.path.exists(savePath):
        return send_file(savePath)
    else:
        return ReJson(4004, body=savePath)


@api.route('/api/file_info', methods=["GET", 'POST'])
def get_file_info():
    file_path = request.args.get("file_path")
    file_path = request.json.get("file_path", file_path)
    if not file_path:
        return ReJson(1002)

    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    wx_path = read_session(g.sf, my_wxid, "wx_path")

    all_file_path = os.path.join(wx_path, file_path)
    if not os.path.exists(all_file_path):
        return ReJson(5002)
    file_name = os.path.basename(all_file_path)
    file_size = os.path.getsize(all_file_path)
    return ReJson(0, {"file_name": file_name, "file_size": str(file_size)})


@api.route('/api/file/<path:filePath>', methods=["GET", 'POST'])
def get_file(filePath):
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    wx_path = read_session(g.sf, my_wxid, "wx_path")

    all_file_path = os.path.join(wx_path, filePath)
    if not os.path.exists(all_file_path):
        return ReJson(5002)
    return send_file(all_file_path)


# end 以上为聊天记录相关api *********************************************************************************************

# start 导出聊天记录 *****************************************************************************************************

@api.route('/api/export_endb', methods=["GET", 'POST'])
def get_export_endb():
    """
    导出加密数据库
    :return:
    """
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    wx_path = read_session(g.sf, my_wxid, "wx_path")
    wx_path = request.json.get("wx_path", wx_path)

    if not wx_path:
        return ReJson(1002, body=f"wx_path is required: {wx_path}")
    if not os.path.exists(wx_path):
        return ReJson(1001, body=f"wx_path not exists: {wx_path}")

    # 分割wx_path的文件名和父目录
    code, wxdbpaths = get_core_db(wx_path)
    if not code:
        return ReJson(2001, body=wxdbpaths)

    outpath = os.path.join(g.tmp_path, "export", my_wxid, "endb")
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    for wxdb in wxdbpaths:
        # 复制wxdb->outpath, os.path.basename(wxdb)
        assert isinstance(outpath, str)  # 为了解决pycharm的警告, 无实际意义
        shutil.copy(wxdb, os.path.join(outpath, os.path.basename(wxdb)))
    return ReJson(0, body=outpath)


@api.route('/api/export_dedb', methods=["GET", "POST"])
def get_export_dedb():
    """
    导出解密数据库
    :return:
    """
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")

    key = request.json.get("key", read_session(g.sf, my_wxid, "key"))
    wx_path = request.json.get("wx_path", read_session(g.sf, my_wxid, "wx_path"))

    if not key:
        return ReJson(1002, body=f"key is required: {key}")
    if not wx_path:
        return ReJson(1002, body=f"wx_path is required: {wx_path}")
    if not os.path.exists(wx_path):
        return ReJson(1001, body=f"wx_path not exists: {wx_path}")

    outpath = os.path.join(g.tmp_path, "export", my_wxid, "dedb")
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    code, merge_save_path = decrypt_merge(wx_path=wx_path, key=key, outpath=outpath)
    time.sleep(1)
    if code:
        return ReJson(0, body=merge_save_path)
    else:
        return ReJson(2001, body=merge_save_path)


@api.route('/api/export_csv', methods=["GET", 'POST'])
def get_export_csv():
    """
    导出csv
    :return:
    """
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")

    wxid = request.json.get("wxid")
    # st_ed_time = request.json.get("datetime", [0, 0])
    if not wxid:
        return ReJson(1002, body=f"username is required: {wxid}")
    # if not isinstance(st_ed_time, list) or len(st_ed_time) != 2:
    #     return ReJson(1002, body=f"datetime is required: {st_ed_time}")
    # start, end = st_ed_time
    # if not isinstance(start, int) or not isinstance(end, int) or start >= end:
    #     return ReJson(1002, body=f"datetime is required: {st_ed_time}")

    outpath = os.path.join(g.tmp_path, "export", my_wxid, "csv", wxid)
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    code, ret = export_csv(wxid, outpath, read_session(g.sf, my_wxid, "merge_path"))
    if code:
        return ReJson(0, ret)
    else:
        return ReJson(2001, body=ret)


@api.route('/api/export_json', methods=["GET", 'POST'])
def get_export_json():
    """
    导出json
    :return:
    """
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")

    wxid = request.json.get("wxid")
    if not wxid:
        return ReJson(1002, body=f"username is required: {wxid}")

    outpath = os.path.join(g.tmp_path, "export", my_wxid, "json", wxid)
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    code, ret = export_json(wxid, outpath, read_session(g.sf, my_wxid, "merge_path"))
    if code:
        return ReJson(0, ret)
    else:
        return ReJson(2001, body=ret)


# @api.route('/api/export', methods=["GET", 'POST'])
# @error9999
# def export():
#     """
#     导出聊天记录
#     :return:
#     """
#     export_type = request.json.get("export_type")
#     start_time = request.json.get("start_time", 0)
#     end_time = request.json.get("end_time", 0)
#     chat_type = request.json.get("chat_type")
#     username = request.json.get("username")
#
#     wx_path = request.json.get("wx_path", read_session(g.sf, "wx_path"))
#     key = request.json.get("key", read_session(g.sf, "key"))
#
#     if not export_type or not isinstance(export_type, str):
#         return ReJson(1002)
#
#     # 导出路径
#     outpath = os.path.join(g.tmp_path, "export", export_type)
#     if not os.path.exists(outpath):
#         os.makedirs(outpath)
#
#     if export_type == "endb":  # 导出加密数据库
#         # 获取微信文件夹路径
#         if not wx_path:
#             return ReJson(1002)
#         if not os.path.exists(wx_path):
#             return ReJson(1001, body=wx_path)
#
#         # 分割wx_path的文件名和父目录
#         code, wxdbpaths = get_core_db(wx_path)
#         if not code:
#             return ReJson(2001, body=wxdbpaths)
#
#         for wxdb in wxdbpaths:
#             # 复制wxdb->outpath, os.path.basename(wxdb)
#             shutil.copy(wxdb, os.path.join(outpath, os.path.basename(wxdb)))
#         return ReJson(0, body=outpath)
#
#     elif export_type == "dedb":
#         if isinstance(start_time, int) and isinstance(end_time, int):
#             msg_path = read_session(g.sf, "msg_path")
#             micro_path = read_session(g.sf, "micro_path")
#             media_path = read_session(g.sf, "media_path")
#             dbpaths = [msg_path, media_path, micro_path]
#             dbpaths = list(set(dbpaths))
#             mergepath = merge_db(dbpaths, os.path.join(outpath, "merge.db"), start_time, end_time)
#             return ReJson(0, body=mergepath)
#             # if msg_path == media_path and msg_path == media_path:
#             #     shutil.copy(msg_path, os.path.join(outpath, "merge.db"))
#             #     return ReJson(0, body=msg_path)
#             # else:
#             #     dbpaths = [msg_path, msg_path, micro_path]
#             #     dbpaths = list(set(dbpaths))
#             #     mergepath = merge_db(dbpaths, os.path.join(outpath, "merge.db"), start_time,  end_time)
#             #     return ReJson(0, body=mergepath)
#         else:
#             return ReJson(1002, body={"start_time": start_time, "end_time": end_time})
#
#     elif export_type == "csv":
#         outpath = os.path.join(outpath, username)
#         if not os.path.exists(outpath):
#             os.makedirs(outpath)
#         code, ret = analyzer.export_csv(username, outpath, read_session(g.sf, "msg_path"))
#         if code:
#             return ReJson(0, ret)
#         else:
#             return ReJson(2001, body=ret)
#     elif export_type == "json":
#         outpath = os.path.join(outpath, username)
#         if not os.path.exists(outpath):
#             os.makedirs(outpath)
#         code, ret = analyzer.export_json(username, outpath, read_session(g.sf, "msg_path"))
#         if code:
#             return ReJson(0, ret)
#         else:
#             return ReJson(2001, body=ret)
#     elif export_type == "html":
#         outpath = os.path.join(outpath, username)
#         if os.path.exists(outpath):
#             shutil.rmtree(outpath)
#         if not os.path.exists(outpath):
#             os.makedirs(outpath)
#         # chat_type_tups = []
#         # for ct in chat_type:
#         #     tup = analyzer.get_name_typeid(ct)
#         #     if tup:
#         #         chat_type_tups += tup
#         # if not chat_type_tups:
#         #     return ReJson(1002)
#
#         # 复制文件 html
#         export_html = os.path.join(os.path.dirname(pywxdump.VERSION_LIST_PATH), "ui", "export")
#         indexhtml_path = os.path.join(export_html, "index.html")
#         assets_path = os.path.join(export_html, "assets")
#         if not os.path.exists(indexhtml_path) or not os.path.exists(assets_path):
#             return ReJson(1001)
#         js_path = ""
#         css_path = ""
#         for file in os.listdir(assets_path):
#             if file.endswith('.js'):
#                 js_path = os.path.join(assets_path, file)
#             elif file.endswith('.css'):
#                 css_path = os.path.join(assets_path, file)
#             else:
#                 continue
#         # 读取html,js,css
#         with open(indexhtml_path, 'r', encoding='utf-8') as f:
#             html = f.read()
#         with open(js_path, 'r', encoding='utf-8') as f:
#             js = f.read()
#         with open(css_path, 'r', encoding='utf-8') as f:
#             css = f.read()
#
#         html = re.sub(r'<script .*?></script>', '', html)  # 删除所有的script标签
#         html = re.sub(r'<link rel="stylesheet" .*?>', '', html)  # 删除所有的link标签
#
#         html = html.replace('</head>', f'<style>{css}</style></head>')
#         html = html.replace('</head>', f'<script type="module" crossorigin>{js}</script></head>')
#         # END 生成index.html
#
#         rdata = func_get_msgs(0, 10000000, username, "", "")
#
#         msg_list = rdata["msg_list"]
#         for i in range(len(msg_list)):
#             if msg_list[i]["type_name"] == "语音":
#                 savePath = msg_list[i]["content"]["src"]
#                 MsgSvrID = savePath.split("_")[-1].replace(".wav", "")
#                 if not savePath:
#                     continue
#                 media_path = read_session(g.sf, "media_path")
#                 wave_data = read_audio(MsgSvrID, is_wave=True, DB_PATH=media_path)
#                 if not wave_data:
#                     continue
#                 # 判断savePath路径的文件夹是否存在
#                 savePath = os.path.join(outpath, savePath)
#                 if not os.path.exists(os.path.dirname(savePath)):
#                     os.makedirs(os.path.dirname(savePath))
#                 with open(savePath, "wb") as f:
#                     f.write(wave_data)
#             elif msg_list[i]["type_name"] == "图片":
#                 img_path = msg_list[i]["content"]["src"]
#                 wx_path = read_session(g.sf, "wx_path")
#                 img_path_all = os.path.join(wx_path, img_path)
#
#                 if os.path.exists(img_path_all):
#                     fomt, md5, out_bytes = read_img_dat(img_path_all)
#                     imgsavepath = os.path.join(outpath, "img", img_path + "_" + ".".join([md5, fomt]))
#                     if not os.path.exists(os.path.dirname(imgsavepath)):
#                         os.makedirs(os.path.dirname(imgsavepath))
#                     with open(imgsavepath, "wb") as f:
#                         f.write(out_bytes)
#                     msg_list[i]["content"]["src"] = os.path.join("img", img_path + "_" + ".".join([md5, fomt]))
#
#         rdata["msg_list"] = msg_list
#         rdata["myuserdata"] = rdata["user_list"][rdata["my_wxid"]]
#         rdata["myuserdata"]["chat_count"] = len(rdata["msg_list"])
#         save_data = rdata
#         save_json_path = os.path.join(outpath, "data")
#         if not os.path.exists(save_json_path):
#             os.makedirs(save_json_path)
#         with open(os.path.join(save_json_path, "msg_user.json"), "w", encoding="utf-8") as f:
#             json.dump(save_data, f, ensure_ascii=False)
#
#         json_base64 = gen_base64(os.path.join(save_json_path, "msg_user.json"))
#         html = html.replace('"./data/msg_user.json"', f'"{json_base64}"')
#
#         with open(os.path.join(outpath, "index.html"), 'w', encoding='utf-8') as f:
#             f.write(html)
#         return ReJson(0, outpath)
#
#     elif export_type == "pdf":
#         pass
#     elif export_type == "docx":
#         pass
#     else:
#         return ReJson(1002)
#
#     return ReJson(9999, "")


# end 导出聊天记录 *******************************************************************************************************

# start 聊天记录分析api **************************************************************************************************

@api.route('/api/date_count', methods=["GET", 'POST'])
@error9999
def get_date_count():
    """
    获取日期统计
    """
    my_wxid = read_session(g.sf, "test", "last")
    if not my_wxid: return ReJson(1001, body="my_wxid is required")
    merge_path = read_session(g.sf, my_wxid, "merge_path")
    date_count = ParsingMSG(merge_path).date_count()
    return ReJson(0, date_count)


@api.route('/api/wordcloud', methods=["GET", 'POST'])
@error9999
def wordcloud():
    pass


# start 这部分为专业工具的api *********************************************************************************************

@api.route('/api/wxinfo', methods=["GET", 'POST'])
@error9999
def get_wxinfo():
    """
    获取微信信息
    :return:
    """
    import pythoncom
    pythoncom.CoInitialize()
    wxinfos = read_info(VERSION_LIST)
    pythoncom.CoUninitialize()
    return ReJson(0, wxinfos)


@api.route('/api/biasaddr', methods=["GET", 'POST'])
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


@api.route('/api/decrypt', methods=["GET", 'POST'])
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


@api.route('/api/merge', methods=["GET", 'POST'])
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
    rdata = merge_db(wxdb_path, out_path)
    return ReJson(0, str(rdata))


# END 这部分为专业工具的api ***********************************************************************************************

# 关于、帮助、设置 *******************************************************************************************************
@api.route('/api/check_update', methods=["GET", 'POST'])
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


@api.route('/api/version', methods=["GET", 'POST'])
@error9999
def version():
    """
    版本
    :return:
    """
    return ReJson(0, pywxdump.__version__)


# END 关于、帮助、设置 ***************************************************************************************************


@api.route('/')
@error9999
def index():
    return render_template('index.html')
