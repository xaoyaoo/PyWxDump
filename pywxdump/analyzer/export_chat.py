# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         export_chat.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/12/03
# -------------------------------------------------------------------------------
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
from functools import wraps

from .utils import get_md5, detach_databases, attach_databases, execute_sql


# from .db_parsing import read_img_dat, decompress_CompressContent, read_audio, parse_xml_string

# from flask import Flask, request, render_template, g, Blueprint


def get_contact_list(MicroMsg_db_path):
    """
    获取联系人列表
    :param MicroMsg_db_path: MicroMsg.db 文件路径
    :return: 联系人列表
    """
    users = []
    # 连接 MicroMsg.db 数据库，并执行查询
    db = sqlite3.connect(MicroMsg_db_path)
    cursor = db.cursor()
    sql = ("SELECT A.UserName, A.NickName, A.Remark,A.Alias,A.Reserved6,B.bigHeadImgUrl "
           "FROM Contact A,ContactHeadImgUrl B "
           "where UserName==usrName "
           "ORDER BY NickName ASC;")
    cursor.execute(sql)
    result = cursor.fetchall()

    for row in result:
        # 获取用户名、昵称、备注和聊天记录数量
        username, nickname, remark, Alias, describe, headImgUrl = row
        users.append(
            {"username": username, "nickname": nickname, "remark": remark, "account": Alias, "describe": describe,
             "headImgUrl": headImgUrl})
    cursor.close()
    db.close()
    return users


def msg_db_connect(func):
    @wraps(func)
    def wrapper(MSG_db_path, *args, **kwargs):
        # 连接 MSG.db 数据库，并执行查询
        if isinstance(MSG_db_path, list):
            # alias, file_path
            databases = {f"MSG{i}": db_path for i, db_path in enumerate(MSG_db_path)}
        elif isinstance(MSG_db_path, str):
            databases = {"MSG": MSG_db_path}
        else:
            raise TypeError("MSG_db_path 类型错误")

        # 连接 MSG_ALL.db 数据库，并执行查询
        if len(databases) > 1:
            db = sqlite3.connect(":memory:")
            attach_databases(db, databases)
        else:
            db = sqlite3.connect(list(databases.values())[0])

        result = func("", db=db, databases=databases, *args, **kwargs)

        # 断开数据库连接
        if len(databases) > 1:
            for alias in databases:
                db.execute(f"DETACH DATABASE {alias}")
            db.close()

        return result

    return wrapper


@msg_db_connect
def get_chat_count(MSG_db_path: [str, list], db=None, databases=None):
    """
    获取聊天记录数量
    :param MSG_db_path: MSG.db 文件路径
    :return: 聊天记录数量列表
    """
    # 构造 SQL 查询，使用 UNION ALL 联合不同数据库的 MSG 表
    union_sql = " UNION ALL ".join(
        f"SELECT StrTalker, COUNT(*) AS ChatCount FROM {alias}.MSG GROUP BY StrTalker" for alias in databases)

    sql = f"SELECT StrTalker, SUM(ChatCount) AS TotalChatCount FROM ({union_sql}) GROUP BY StrTalker ORDER BY TotalChatCount DESC"

    chat_counts = []
    result = execute_sql(db, sql)
    for row in result:
        username, chat_count = row
        row_data = {"username": username, "chat_count": chat_count}
        chat_counts.append(row_data)
    return chat_counts


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


if __name__ == '__main__':
    msg_all = ""
    a = get_contact_list(msg_all)
    print(a)
