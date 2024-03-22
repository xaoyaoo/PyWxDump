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
import csv
import re
import sqlite3
import os
import json
import time
from functools import wraps

from .utils import get_md5, attach_databases, execute_sql, get_type_name, match_BytesExtra, DBPool
from .db_parsing import parse_xml_string, decompress_CompressContent, read_BytesExtra


def get_contact(MicroMsg_db_path, wx_id):
    """
    获取联系人信息
    :param MicroMsg_db_path: MicroMsg.db 文件路径
    :param wx_id: 微信id
    :return: 联系人信息
    """
    with DBPool(MicroMsg_db_path) as db:
        # 获取username是wx_id的用户
        sql = ("SELECT A.UserName, A.NickName, A.Remark,A.Alias,A.Reserved6,B.bigHeadImgUrl "
               "FROM Contact A,ContactHeadImgUrl B "
               f"WHERE A.UserName = '{wx_id}' AND A.UserName = B.usrName "
               "ORDER BY NickName ASC;")
        result = execute_sql(db, sql)
        print('联系人信息：', result)
        if not result:
            print('居然没找到！')
            print(wx_id)
            return None
        return {"username": result[0], "nickname": result[1], "remark": result[2], "account": result[3],
                "describe": result[4], "headImgUrl": result[5]}


def get_contact_list(MicroMsg_db_path, OpenIMContact_db_path=None):
    """
    获取联系人列表
    :param MicroMsg_db_path: MicroMsg.db 文件路径
    :return: 联系人列表
    """
    users = []
    # 连接 MicroMsg.db 数据库，并执行查询
    with DBPool(MicroMsg_db_path) as db:
        sql = ("SELECT A.UserName, A.NickName, A.Remark,A.Alias,A.Reserved6,B.bigHeadImgUrl "
               "FROM Contact A,ContactHeadImgUrl B "
               "where UserName==usrName "
               "ORDER BY NickName ASC;")
        result = execute_sql(db, sql)
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            username, nickname, remark, Alias, describe, headImgUrl = row
            users.append(
                {"username": username, "nickname": nickname, "remark": remark, "account": Alias, "describe": describe,
                 "headImgUrl": headImgUrl})
        # return users
    if OpenIMContact_db_path:
        with DBPool(OpenIMContact_db_path) as db:
            sql = ("SELECT A.UserName, A.NickName, A.Remark,A.BigHeadImgUrl FROM OpenIMContact A "
                   "ORDER BY NickName ASC;")
            result = execute_sql(db, sql)
            for row in result:
                # 获取用户名、昵称、备注和聊天记录数量
                username, nickname, remark, headImgUrl = row
                users.append(
                    {"username": username, "nickname": nickname, "remark": remark, "account": "", "describe": "",
                     "headImgUrl": headImgUrl})
    return users

def get_chatroom_list(MicroMsg_db_path):
    """
    获取群聊列表
    :param MicroMsg_db_path: MicroMsg.db 文件路径
    :return: 群聊列表
    """
    rooms = []
    # 连接 MicroMsg.db 数据库，并执行查询
    with DBPool(MicroMsg_db_path) as db:
        sql = ("SELECT A.ChatRoomName,A.UserNameList, A.DisplayNameList, B.Announcement,B.AnnouncementEditor "
               "FROM ChatRoom A,ChatRoomInfo B "
               "where A.ChatRoomName==B.ChatRoomName "
               "ORDER BY A.ChatRoomName ASC;")
        result = execute_sql(db, sql)
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            ChatRoomName, UserNameList, DisplayNameList, Announcement, AnnouncementEditor = row
            UserNameList = UserNameList.split("^G")
            DisplayNameList = DisplayNameList.split("^G")
            rooms.append(
                {"ChatRoomName": ChatRoomName, "UserNameList": UserNameList, "DisplayNameList": DisplayNameList,
                 "Announcement": Announcement, "AnnouncementEditor": AnnouncementEditor})
        return rooms


def get_room_user_list(MSG_db_path, selected_talker):
    """
    获取群聊中包含的所有用户列表
    :param MSG_db_path: MSG.db 文件路径
    :param selected_talker: 选中的聊天对象 wxid
    :return: 聊天用户列表
    """

    # 连接 MSG_ALL.db 数据库，并执行查询
    with DBPool(MSG_db_path) as db1:
        sql = (
            "SELECT localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType,CreateTime,MsgSvrID,DisplayContent,CompressContent,BytesExtra,ROW_NUMBER() OVER (ORDER BY CreateTime ASC) AS id "
            "FROM MSG WHERE StrTalker=? "
            "ORDER BY CreateTime ASC")

        result1 = execute_sql(db1, sql, (selected_talker,))
        user_list = []
        read_user_wx_id = []
        for row in result1:
            localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType, CreateTime, MsgSvrID, DisplayContent, CompressContent, BytesExtra, id = row
            bytes_extra = read_BytesExtra(BytesExtra)
            if bytes_extra:
                try:
                    talker = bytes_extra['3'][0]['2'].decode('utf-8', errors='ignore')
                except:
                    continue
            if talker in read_user_wx_id:
                continue
            user = get_contact(MSG_db_path, talker)
            if not user:
                continue
            user_list.append(user)
            read_user_wx_id.append(talker)
        return user_list


def get_msg_list(MSG_db_path, selected_talker="", start_index=0, page_size=500):
    """
    获取聊天记录列表
    :param MSG_db_path: MSG.db 文件路径
    :param selected_talker: 选中的聊天对象 wxid
    :param start_index: 开始索引
    :param page_size: 每页数量
    :return: 聊天记录列表
    """

    # 连接 MSG_ALL.db 数据库，并执行查询
    with DBPool(MSG_db_path) as db1:
        if selected_talker:
            sql = (
                "SELECT localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType,CreateTime,MsgSvrID,DisplayContent,CompressContent,BytesExtra,ROW_NUMBER() OVER (ORDER BY CreateTime ASC) AS id "
                "FROM MSG WHERE StrTalker=? "
                "ORDER BY CreateTime ASC LIMIT ?,?")
            result1 = execute_sql(db1, sql, (selected_talker, start_index, page_size))
        else:
            sql = (
                "SELECT localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType,CreateTime,MsgSvrID,DisplayContent,CompressContent,BytesExtra,ROW_NUMBER() OVER (ORDER BY CreateTime ASC) AS id "
                "FROM MSG ORDER BY CreateTime ASC LIMIT ?,?")
            result1 = execute_sql(db1, sql, (start_index, page_size))

        data = []
        for row in result1:
            localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType, CreateTime, MsgSvrID, DisplayContent, CompressContent, BytesExtra, id = row
            CreateTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(CreateTime))

            type_id = (Type, SubType)
            type_name = get_type_name(type_id)

            content = {"src": "", "msg": StrContent}

            if type_id == (1, 0):  # 文本
                content["msg"] = StrContent

            elif type_id == (3, 0):  # 图片
                DictExtra = read_BytesExtra(BytesExtra)
                DictExtra = str(DictExtra)
                match = re.search(r"FileStorage(.*?)'", DictExtra)
                if match:
                    img_path = match.group(0).replace("'", "")
                    img_path = [i for i in img_path.split("\\") if i]
                    img_path = os.path.join(*img_path)
                    content["src"] = img_path
                else:
                    content["src"] = ""
                content["msg"] = "图片"
            elif type_id == (34, 0):
                tmp_c = parse_xml_string(StrContent)
                voicelength = tmp_c.get("voicemsg", {}).get("voicelength", "")
                transtext = tmp_c.get("voicetrans", {}).get("transtext", "")
                if voicelength.isdigit():
                    voicelength = int(voicelength) / 1000
                    voicelength = f"{voicelength:.2f}"
                content[
                    "msg"] = f"语音时长：{voicelength}秒\n翻译结果：{transtext}" if transtext else f"语音时长：{voicelength}秒"
                content["src"] = os.path.join("audio", f"{StrTalker}",
                                              f"{CreateTime.replace(':', '-').replace(' ', '_')}_{IsSender}_{MsgSvrID}.wav")
            elif type_id == (43, 0):  # 视频
                DictExtra = read_BytesExtra(BytesExtra)
                DictExtra = str(DictExtra)
                match = re.search(r"FileStorage(.*?)'", DictExtra)
                if match:
                    video_path = match.group(0).replace("'", "")
                    content["src"] = video_path
                else:
                    content["src"] = ""
                content["msg"] = "视频"

            elif type_id == (47, 0):  # 动画表情
                content_tmp = parse_xml_string(StrContent)
                cdnurl = content_tmp.get("emoji", {}).get("cdnurl", "")
                if cdnurl:
                    content = {"src": cdnurl, "msg": "表情"}

            elif type_id == (49, 0):
                DictExtra = read_BytesExtra(BytesExtra)
                url = match_BytesExtra(DictExtra)
                content["src"] = url
                file_name = os.path.basename(url)
                content["msg"] = file_name

            elif type_id == (49, 19):  # 合并转发的聊天记录
                CompressContent = decompress_CompressContent(CompressContent)
                content_tmp = parse_xml_string(CompressContent)
                title = content_tmp.get("appmsg", {}).get("title", "")
                des = content_tmp.get("appmsg", {}).get("des", "")
                recorditem = content_tmp.get("appmsg", {}).get("recorditem", "")
                recorditem = parse_xml_string(recorditem)
                content["msg"] = f"{title}\n{des}"
                content["src"] = recorditem

            elif type_id == (49, 2000):  # 转账消息
                CompressContent = decompress_CompressContent(CompressContent)
                content_tmp = parse_xml_string(CompressContent)
                feedesc = content_tmp.get("appmsg", {}).get("wcpayinfo", {}).get("feedesc", "")
                content["msg"] = f"转账：{feedesc}"
                content["src"] = ""

            elif type_id[0] == 49 and type_id[1] != 0:
                DictExtra = read_BytesExtra(BytesExtra)
                url = match_BytesExtra(DictExtra)
                content["src"] = url
                content["msg"] = type_name

            elif type_id == (50, 0):  # 语音通话
                content["msg"] = "语音/视频通话[%s]" % DisplayContent

            # elif type_id == (10000, 0):
            #     content["msg"] = StrContent
            # elif type_id == (10000, 4):
            #     content["msg"] = StrContent
            # elif type_id == (10000, 8000):
            #     content["msg"] = StrContent

            talker = "未知"
            if IsSender == 1:
                talker = "我"
            else:
                if StrTalker.endswith("@chatroom"):
                    bytes_extra = read_BytesExtra(BytesExtra)
                    if bytes_extra:
                        try:
                            talker = bytes_extra['3'][0]['2'].decode('utf-8', errors='ignore')
                            if "publisher-id" in talker:
                                talker = "系统"
                        except:
                            pass
                else:
                    talker = StrTalker

            row_data = {"MsgSvrID": str(MsgSvrID), "type_name": type_name, "is_sender": IsSender, "talker": talker,
                        "room_name": StrTalker, "content": content, "CreateTime": CreateTime, "id": id}
            data.append(row_data)
        return data


def get_chat_count(MSG_db_path: [str, list], username: str = ""):
    """
    获取聊天记录数量
    :param MSG_db_path: MSG.db 文件路径
    :return: 聊天记录数量列表
    """
    if username:
        sql = f"SELECT StrTalker,COUNT(*) FROM MSG WHERE StrTalker='{username}';"
    else:
        sql = f"SELECT StrTalker, COUNT(*) FROM MSG GROUP BY StrTalker ORDER BY COUNT(*) DESC;"

    with DBPool(MSG_db_path) as db1:
        result = execute_sql(db1, sql)
        chat_counts = {}
        for row in result:
            username, chat_count = row
            chat_counts[username] = chat_count
        return chat_counts


def get_all_chat_count(MSG_db_path: [str, list]):
    """
    获取聊天记录总数量
    :param MSG_db_path: MSG.db 文件路径
    :return: 聊天记录数量
    """
    sql = f"SELECT COUNT(*) FROM MSG;"
    with DBPool(MSG_db_path) as db1:
        result = execute_sql(db1, sql)
        if result and len(result) > 0:
            chat_counts = result[0][0]
            return chat_counts
        return 0


def export_csv(username, outpath, MSG_ALL_db_path, page_size=5000):
    if not os.path.exists(outpath):
        outpath = os.path.join(os.getcwd(), "export" + os.sep + username)
        if not os.path.exists(outpath):
            os.makedirs(outpath)
    count = get_chat_count(MSG_ALL_db_path, username)
    chatCount = count.get(username, 0)
    if chatCount == 0:
        return False, "没有聊天记录"
    if page_size > chatCount:
        page_size = chatCount + 1
    for i in range(0, chatCount, page_size):
        start_index = i
        data = get_msg_list(MSG_ALL_db_path, username, start_index, page_size)
        if len(data) == 0:
            return False, "没有聊天记录"
        save_path = os.path.join(outpath, f"{username}_{i}_{i + page_size}.csv")
        with open(save_path, "w", encoding="utf-8", newline='') as f:
            csv_writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(["id", "MsgSvrID", "type_name", "is_sender", "talker", "room_name", "content",
                                 "CreateTime"])
            for row in data:
                id = row.get("id", "")
                MsgSvrID = row.get("MsgSvrID", "")
                type_name = row.get("type_name", "")
                is_sender = row.get("is_sender", "")
                talker = row.get("talker", "")
                room_name = row.get("room_name", "")
                content = row.get("content", "")
                CreateTime = row.get("CreateTime", "")

                content = json.dumps(content, ensure_ascii=False)
                csv_writer.writerow([id, MsgSvrID, type_name, is_sender, talker, room_name, content, CreateTime])

    return True, f"导出成功: {outpath}"


def export_json(username, outpath, MSG_ALL_db_path):
    if not os.path.exists(outpath):
        outpath = os.path.join(os.getcwd(), "export" + os.sep + username)
        if not os.path.exists(outpath):
            os.makedirs(outpath)
    count = get_chat_count(MSG_ALL_db_path, username)
    chatCount = count.get(username, 0)
    if chatCount == 0:
        return False, "没有聊天记录"
    page_size = chatCount + 1
    for i in range(0, chatCount, page_size):
        start_index = i
        data = get_msg_list(MSG_ALL_db_path, username, start_index, page_size)
        if len(data) == 0:
            return False, "没有聊天记录"
        save_path = os.path.join(outpath, f"{username}_{i}_{i + page_size}.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    return True, f"导出成功: {outpath}"


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
