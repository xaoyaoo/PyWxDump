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
from pywxdump import analyzer, read_img_dat
from pywxdump.api.rjson import ReJson, RqJson
from flask_cors import CORS

# from flask_cors import CORS

app = Flask(__name__, static_folder='../ui/web/dist', static_url_path='/')

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # 允许所有域名跨域


@app.route('/api/init', methods=["GET", 'POST'])
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


@app.route('/api/contact_list', methods=["GET", 'POST'])
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


@app.route('/api/chat_count', methods=["GET", 'POST'])
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
        contact_list = analyzer.get_chat_count(msg_path)
        return ReJson(0, contact_list)
    except Exception as e:
        return ReJson(9999, msg=str(e))


@app.route('/api/contact_count_list', methods=["GET", 'POST'])
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


@app.route('/api/msgs', methods=["GET", 'POST'])
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


@app.route('/api/img', methods=["GET", 'POST'])
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

@app.route('/api/audio', methods=["GET", 'POST'])
def get_audio():
    pass

if __name__ == '__main__':
    @app.before_request
    def before_request():
        path = r"D:\_code\py_code\test\a2023\b0821wxdb\merge_wfwx_db\kkWxMsg\MSG_all.db"
        g.msg_path = path
        g.micro_path = path
        g.media_path = path
        g.wxid_path = r"C:\Users\xaoyo\Documents\Tencent\WeChat Files\wxid_vzzcn5fevion22"
        g.my_wxid = "wxid_vzzcn5fevion22"
        g.tmp_path = "dist"  # 临时文件夹,用于存放图片等
        g.user_list = []


    app.run(host='0.0.0.0', port=5000, debug=True)
