# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         GUI.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/11/10
# -------------------------------------------------------------------------------
import base64
import sqlite3
import os
import json
import time
import hashlib
from pywxdump.analyzer import read_img_dat, decompress_CompressContent, read_audio, parse_xml_string

from flask import Flask, request, render_template, g, Blueprint


def get_md5(s):
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


def get_user_list(MSG_ALL_db_path, MicroMsg_db_path):
    users = []
    # 连接 MSG_ALL.db 数据库，并执行查询
    db1 = sqlite3.connect(MSG_ALL_db_path)
    cursor1 = db1.cursor()
    cursor1.execute("SELECT StrTalker, COUNT(*) AS ChatCount FROM MSG GROUP BY StrTalker ORDER BY ChatCount DESC")
    result = cursor1.fetchall()

    for row in result:
        # 获取用户名、昵称、备注和聊天记录数量
        db2 = sqlite3.connect(MicroMsg_db_path)
        cursor2 = db2.cursor()
        cursor2.execute("SELECT UserName, NickName, Remark FROM Contact WHERE UserName=?", (row[0],))
        result2 = cursor2.fetchone()
        if result2:
            username, nickname, remark = result2
            chat_count = row[1]

            # 拼接四列数据为元组
            row_data = {"username": username, "nickname": nickname, "remark": remark, "chat_count": chat_count,
                        "isChatRoom": username.startswith("@chatroom")}
            users.append(row_data)
        cursor2.close()
        db2.close()
    cursor1.close()
    db1.close()
    return users


def load_base64_audio_data(MsgSvrID, MediaMSG_all_db_path):
    wave_data = read_audio(MsgSvrID, is_wave=True, DB_PATH=MediaMSG_all_db_path)
    if not wave_data:
        return ""
    video_base64 = base64.b64encode(wave_data).decode("utf-8")
    video_data = f"data:audio/wav;base64,{video_base64}"
    return video_data


def load_base64_img_data(start_time, end_time, username_md5, FileStorage_path):
    """
    获取图片的base64数据
    :param start_time: 开始时间戳
    :param end_time:  结束时间戳
    :param username_md5: 用户名的md5值
    :return:
    """
    # 获取CreateTime的最大值日期
    min_time = time.strftime("%Y-%m", time.localtime(start_time))
    max_time = time.strftime("%Y-%m", time.localtime(end_time))
    img_path = os.path.join(FileStorage_path, "MsgAttach", username_md5, "Image") if FileStorage_path else ""
    if not os.path.exists(img_path):
        return {}
    # print(min_time, max_time, img_path)
    paths = []
    for root, path, files in os.walk(img_path):
        for p in path:
            if p >= min_time and p <= max_time:
                paths.append(os.path.join(root, p))
    # print(paths)
    img_md5_data = {}
    for path in paths:
        for root, path, files in os.walk(path):
            for file in files:
                if file.endswith(".dat"):
                    file_path = os.path.join(root, file)
                    fomt, md5, out_bytes = read_img_dat(file_path)
                    out_bytes = base64.b64encode(out_bytes).decode("utf-8")
                    img_md5_data[md5] = f"data:{fomt};base64,{out_bytes}"
    return img_md5_data


def load_chat_records(selected_talker, start_index, page_size, user_list, MSG_ALL_db_path, MediaMSG_all_db_path,
                      FileStorage_path):
    username = user_list.get("username", "")
    username_md5 = get_md5(username)
    type_name_dict = {
        1: {0: "文本"},
        3: {0: "图片"},
        34: {0: "语音"},
        43: {0: "视频"},
        47: {0: "动画表情"},
        49: {0: "文本", 1: "类似文字消息而不一样的消息", 5: "卡片式链接", 6: "文件", 8: "用户上传的 GIF 表情",
             19: "合并转发的聊天记录", 33: "分享的小程序", 36: "分享的小程序", 57: "带有引用的文本消息",
             63: "视频号直播或直播回放等",
             87: "群公告", 88: "视频号直播或直播回放等", 2000: "转账消息", 2003: "赠送红包封面"},
        50: {0: "语音通话"},
        10000: {0: "系统通知", 4: "拍一拍", 8000: "系统通知"}
    }

    # 连接 MSG_ALL.db 数据库，并执行查询
    db1 = sqlite3.connect(MSG_ALL_db_path)
    cursor1 = db1.cursor()

    cursor1.execute(
        "SELECT localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType,CreateTime,MsgSvrID,DisplayContent,CompressContent FROM MSG WHERE StrTalker=? ORDER BY CreateTime ASC LIMIT ?,?",
        (selected_talker, start_index, page_size))
    result1 = cursor1.fetchall()

    cursor1.close()
    db1.close()

    img_md5_data = load_base64_img_data(result1[0][7], result1[-1][7], username_md5, FileStorage_path)  # 获取图片的base64数据

    data = []
    for row in result1:
        localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType, CreateTime, MsgSvrID, DisplayContent, CompressContent = row
        CreateTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(CreateTime))

        type_name = type_name_dict.get(Type, {}).get(SubType, "未知")

        content = {"src": "", "msg": "", "style": ""}

        if Type == 47 and SubType == 0:  # 动画表情
            content_tmp = parse_xml_string(StrContent)
            cdnurl = content_tmp.get("emoji", {}).get("cdnurl", "")
            # md5 = content_tmp.get("emoji", {}).get("md5", "")
            if cdnurl:
                content = {"src": cdnurl, "msg": "表情", "style": "width: 100px; height: 100px;"}

        elif Type == 49 and SubType == 57:  # 带有引用的文本消息
            CompressContent = CompressContent.rsplit(b'\x00', 1)[0]
            content["msg"] = decompress_CompressContent(CompressContent)
            try:
                content["msg"] = content["msg"].decode("utf-8")
                content["msg"] = parse_xml_string(content["msg"])
                content["msg"] = json.dumps(content["msg"], ensure_ascii=False)
            except Exception as e:
                content["msg"] = "[带有引用的文本消息]解析失败"
        elif Type == 34 and SubType == 0:  # 语音
            tmp_c = parse_xml_string(StrContent)
            voicelength = tmp_c.get("voicemsg", {}).get("voicelength", "")
            transtext = tmp_c.get("voicetrans", {}).get("transtext", "")
            if voicelength.isdigit():
                voicelength = int(voicelength) / 1000
                voicelength = f"{voicelength:.2f}"
            content["msg"] = f"语音时长：{voicelength}秒\n翻译结果：{transtext}"

            src = load_base64_audio_data(MsgSvrID, MediaMSG_all_db_path=MediaMSG_all_db_path)
            content["src"] = src
        elif Type == 3 and SubType == 0:  # 图片
            xml_content = parse_xml_string(StrContent)
            md5 = xml_content.get("img", {}).get("md5", "")
            if md5:
                content["src"] = img_md5_data.get(md5, "")
            else:
                content["src"] = ""
            content["msg"] = "图片"

        else:
            content["msg"] = StrContent

        row_data = {"MsgSvrID": MsgSvrID, "type_name": type_name, "is_sender": IsSender,
                    "content": content, "CreateTime": CreateTime}
        data.append(row_data)
    return data


def export_html(user, outpath, MSG_ALL_db_path, MediaMSG_all_db_path, FileStorage_path, page_size=500):
    name_save = user.get("remark", user.get("nickname", user.get("username", "")))
    username = user.get("username", "")

    chatCount = user.get("chat_count", 0)
    if chatCount == 0:
        return False, "没有聊天记录"

    for i in range(0, chatCount, page_size):
        start_index = i
        data = load_chat_records(username, start_index, page_size, user, MSG_ALL_db_path, MediaMSG_all_db_path,
                                 FileStorage_path)
        if len(data) == 0:
            break
        save_path = os.path.join(outpath, f"{name_save}_{int(i / page_size)}.html")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(render_template("chat.html", msgs=data))
    return True, f"导出成功{outpath}"


def export(username, outpath, MSG_ALL_db_path, MicroMsg_db_path, MediaMSG_all_db_path, FileStorage_path):
    if not os.path.exists(outpath):
        outpath = os.path.join(os.getcwd(), "export" + os.sep + username)
        if not os.path.exists(outpath):
            os.makedirs(outpath)

    USER_LIST = get_user_list(MSG_ALL_db_path, MicroMsg_db_path)
    user = list(filter(lambda x: x["username"] == username, USER_LIST))

    if username and len(user) > 0:
        user = user[0]
        return export_html(user, outpath, MSG_ALL_db_path, MediaMSG_all_db_path, FileStorage_path)


app_show_chat = Blueprint('show_chat_main', __name__, template_folder='templates')
app_show_chat.debug = False


# 主页 - 显示用户列表
@app_show_chat.route('/')
def index():
    g.USER_LIST = get_user_list(g.MSG_ALL_db_path, g.MicroMsg_db_path)
    return render_template("index.html", users=g.USER_LIST)


# 获取聊天记录
@app_show_chat.route('/get_chat_data', methods=["GET", 'POST'])
def get_chat_data():
    username = request.args.get("username", "")
    user = list(filter(lambda x: x["username"] == username, g.USER_LIST))

    if username and len(user) > 0:
        user = user[0]

        limit = int(request.args.get("limit", 100))  # 每页显示的条数
        page = int(request.args.get("page", user.get("chat_count", limit) / limit))  # 当前页数

        start_index = (page - 1) * limit
        page_size = limit

        data = load_chat_records(username, start_index, page_size, user, g.MSG_ALL_db_path, g.MediaMSG_all_db_path,
                                 g.FileStorage_path)
        return render_template("chat.html", msgs=data)
    else:
        return "error"


# 聊天记录导出为html
@app_show_chat.route('/export_chat_data', methods=["GET", 'POST'])
def get_export():
    username = request.args.get("username", "")

    user = list(filter(lambda x: x["username"] == username, g.USER_LIST))

    if username and len(user) > 0:
        user = user[0]
        n = f"{user.get('username', '')}_{user.get('nickname', '')}_{user.get('remark', '')}"
        outpath = os.path.join(os.getcwd(), "export" + os.sep + n)
        if not os.path.exists(outpath):
            os.makedirs(outpath)

        ret = export_html(user, outpath, g.MSG_ALL_db_path, g.MediaMSG_all_db_path, g.FileStorage_path, page_size=200)
        if ret[0]:
            return ret[1]
        else:
            return ret[1]
    else:
        return "error"
