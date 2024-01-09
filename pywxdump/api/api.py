# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         chat_api.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/01/02
# -------------------------------------------------------------------------------
import base64
import os

from flask import Flask, request, render_template, g, Blueprint, send_file
from pywxdump import analyzer, read_img_dat, read_audio
from pywxdump.api.rjson import ReJson, RqJson

# app = Flask(__name__, static_folder='../ui/web/dist', static_url_path='/')

api = Blueprint('api', __name__, template_folder='../ui/web')
api.debug = False


@api.route('/api/init', methods=["GET", 'POST'])
def init():
    """
    初始化
    :return:
    """
    rdata = {
        "msg_path": "",
        "micro_path": "",
        "media_path": "",
        "filestorage_path": "",
    }
    return ReJson(0, rdata)


@api.route('/api/contact_list', methods=["GET", 'POST'])
def contact_list():
    """
    获取联系人列表
    :return:
    """
    try:
        # 获取联系人列表
        # 从header中读取micro_path
        micro_path = request.headers.get("micro_path")
        if not micro_path:
            micro_path = g.micro_path
        start = request.json.get("start")
        limit = request.json.get("limit")

        contact_list = analyzer.get_contact_list(micro_path)
        g.user_list = contact_list
        if limit:
            contact_list = contact_list[int(start):int(start) + int(limit)]
        return ReJson(0, contact_list)
    except Exception as e:
        return ReJson(9999, msg=str(e))


@api.route('/api/chat_count', methods=["GET", 'POST'])
def chat_count():
    """
    获取联系人列表
    :return:
    """
    try:
        # 获取联系人列表
        # 从header中读取micro_path
        msg_path = request.headers.get("msg_path")
        if not msg_path:
            msg_path = g.msg_path
        username = request.json.get("username", "")
        contact_list = analyzer.get_chat_count(msg_path, username)
        return ReJson(0, contact_list)
    except Exception as e:
        return ReJson(9999, msg=str(e))


@api.route('/api/contact_count_list', methods=["GET", 'POST'])
def contact_count_list():
    """
    获取联系人列表
    :return:
    """
    try:
        # 获取联系人列表
        # 从header中读取micro_path
        msg_path = request.headers.get("msg_path")
        micro_path = request.headers.get("micro_path")
        if not msg_path:
            msg_path = g.msg_path
        if not micro_path:
            micro_path = g.micro_path
        start = request.json.get("start")
        limit = request.json.get("limit")
        word = request.json.get("word", "")

        contact_list = analyzer.get_contact_list(micro_path)
        chat_count = analyzer.get_chat_count(msg_path)
        for contact in contact_list:
            contact["chat_count"] = chat_count.get(contact["username"], 0)
        # 去重
        contact_list = [dict(t) for t in {tuple(d.items()) for d in contact_list}]
        # 降序
        contact_list = sorted(contact_list, key=lambda x: x["chat_count"], reverse=True)

        g.user_list = contact_list

        if word and word != "" and word != "undefined" and word != "null":
            contact_list = [contact for contact in contact_list if
                            word in contact["account"] or word in contact["describe"] or word in contact[
                                "nickname"] or word in contact["remark"] or word in contact["username"]]
        if limit:
            contact_list = contact_list[int(start):int(start) + int(limit)]
        return ReJson(0, contact_list)
    except Exception as e:
        return ReJson(9999, msg=str(e))


@api.route('/api/msgs', methods=["GET", 'POST'])
def get_msgs():
    msg_path = request.headers.get("msg_path")
    micro_path = request.headers.get("micro_path")
    if not msg_path:
        msg_path = g.msg_path
    if not micro_path:
        micro_path = g.micro_path
    start = request.json.get("start")
    limit = request.json.get("limit")
    wxid = request.json.get("wxid")
    msg_list = analyzer.get_msg_list(msg_path, wxid, start_index=start, page_size=limit)
    # row_data = {"MsgSvrID": MsgSvrID, "type_name": type_name, "is_sender": IsSender, "talker": talker,
    #             "room_name": StrTalker, "content": content, "CreateTime": CreateTime}
    contact_list = analyzer.get_contact_list(micro_path)

    userlist = {}
    if wxid.endswith("@chatroom"):
        # 群聊
        talkers = [msg["talker"] for msg in msg_list] + [wxid, g.my_wxid]
        talkers = list(set(talkers))
        for user in contact_list:
            if user["username"] in talkers:
                userlist[user["username"]] = user
    else:
        # 单聊
        for user in contact_list:
            if user["username"] == wxid or user["username"] == g.my_wxid:
                userlist[user["username"]] = user
            if len(userlist) == 2:
                break

    return ReJson(0, {"msg_list": msg_list, "user_list": userlist, "my_wxid": g.my_wxid})


@api.route('/api/img', methods=["GET", 'POST'])
def get_img():
    """
    获取图片
    :return:
    """
    img_path = request.args.get("img_path")
    img_path = request.json.get("img_path", img_path)
    if not img_path:
        return ReJson(1002)
    img_path_all = os.path.join(g.wxid_path, img_path)
    if os.path.exists(img_path_all):
        fomt, md5, out_bytes = read_img_dat(img_path_all)
        out_bytes = base64.b64encode(out_bytes).decode("utf-8")
        out_bytes = f"data:{fomt};base64,{out_bytes}"
        return ReJson(0, out_bytes)
    else:
        return ReJson(1001)


@api.route('/api/audio', methods=["GET", 'POST'])
def get_audio():
    MsgSvrID = request.args.get("MsgSvrID")
    MsgSvrID = request.json.get("MsgSvrID", MsgSvrID)
    if not MsgSvrID:
        return ReJson(1002)
    wave_data = read_audio(MsgSvrID, is_wave=True, DB_PATH=g.media_path)
    if not wave_data:
        return ReJson(1001)
    video_base64 = base64.b64encode(wave_data).decode("utf-8")
    video_data = f"data:audio/wav;base64,{video_base64}"
    return ReJson(0, video_data)


@api.route('/')
def index():
    return render_template('index.html')
