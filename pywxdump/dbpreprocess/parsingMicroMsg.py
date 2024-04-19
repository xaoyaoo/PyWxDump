# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parsingMicroMsg.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
import logging

from .dbbase import DatabaseBase
from .utils import timestamp2str, bytes2str

import blackboxprotobuf


class ParsingMicroMsg(DatabaseBase):
    _class_name = "MicroMsg"

    def __init__(self, db_path):
        super().__init__(db_path)

    def get_BytesExtra(self, BytesExtra):
        if BytesExtra is None or not isinstance(BytesExtra, bytes):
            return None
        try:
            deserialize_data, message_type = blackboxprotobuf.decode_message(BytesExtra)
            return deserialize_data
        except Exception as e:
            return None

    def ChatRoom_RoomData(self, RoomData):
        # 读取群聊数据,主要为 wxid，以及对应昵称
        if RoomData is None or not isinstance(RoomData, bytes):
            return None
        try:
            data = self.get_BytesExtra(RoomData)
            bytes2str(data)
            return data
        except Exception as e:
            return None

    def wxid2userinfo(self, wxid):
        """
        获取单个联系人信息
        :param wxid: 微信id
        :return: 联系人信息
        """
        if isinstance(wxid, str):
            wxid = [wxid]
        elif isinstance(wxid, list):
            wxid = wxid
        else:
            return {}
        wxid = "','".join(wxid)
        wxid = f"'{wxid}'"
        # 获取username是wx_id的用户
        sql = ("SELECT A.UserName, A.NickName, A.Remark,A.Alias,A.Reserved6,B.bigHeadImgUrl "
               "FROM Contact A,ContactHeadImgUrl B "
               f"WHERE A.UserName = B.usrName AND A.UserName in ({wxid}) "
               "ORDER BY NickName ASC;")
        result = self.execute_sql(sql)
        if not result:
            return {}
        users = {}
        for row in result:
            # 获取wxid,昵称，备注，描述，头像
            username, nickname, remark, Alias, describe, headImgUrl = row
            users[username] = {"wxid": username, "nickname": nickname, "remark": remark, "account": Alias,
                               "describe": describe, "headImgUrl": headImgUrl}
        return users

    def user_list(self, word=None):
        """
        获取联系人列表
        :param MicroMsg_db_path: MicroMsg.db 文件路径
        :return: 联系人列表
        """
        users = []
        sql = (
            "SELECT A.UserName, A.NickName, A.Remark,A.Alias,A.Reserved6,B.bigHeadImgUrl "
            "FROM Contact A left join ContactHeadImgUrl B on A.UserName==B.usrName "
            "ORDER BY A.NickName DESC;")
        if word:
            sql = sql.replace("ORDER BY A.NickName DESC;",
                              f"where "
                              f"A.UserName LIKE '%{word}%' "
                              f"OR A.NickName LIKE '%{word}%' "
                              f"OR A.Remark LIKE '%{word}%' "
                              f"OR A.Alias LIKE '%{word}%' "
                              # f"OR A.Reserved6 LIKE '%{word}%' "
                              "ORDER BY A.NickName DESC;")
        result = self.execute_sql(sql)
        if not result:
            return []
        for row in result:
            # 获取wxid,昵称，备注，描述，头像
            username, nickname, remark, Alias, describe, headImgUrl = row
            users.append(
                {"wxid": username, "nickname": nickname, "remark": remark, "account": Alias,
                 "describe": describe, "headImgUrl": headImgUrl})
        return users

    def recent_chat_wxid(self):
        """
        获取最近聊天的联系人
        :return: 最近聊天的联系人
        """
        users = []
        sql = (
            "SELECT C.Username, C.LastReadedCreateTime,C.LastReadedSvrId "
            "FROM ChatInfo C "
            "ORDER BY C.LastReadedCreateTime DESC;")
        result = self.execute_sql(sql)
        if not result:
            return []
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            username, LastReadedCreateTime, LastReadedSvrId = row
            LastReadedCreateTime = timestamp2str(LastReadedCreateTime / 1000) if LastReadedCreateTime else None
            users.append(
                {"wxid": username, "LastReadedCreateTime": LastReadedCreateTime, "LastReadedSvrId": LastReadedSvrId})
        return users

    def chatroom_list(self, roomwxid=None):
        """
        获取群聊列表
        :param MicroMsg_db_path: MicroMsg.db 文件路径
        :return: 群聊列表
        """
        rooms = []
        # 连接 MicroMsg.db 数据库，并执行查询
        sql = (
            "SELECT A.ChatRoomName,A.UserNameList, A.DisplayNameList,A.RoomData, B.Announcement,B.AnnouncementEditor "
            "FROM ChatRoom A,ChatRoomInfo B "
            "where A.ChatRoomName==B.ChatRoomName "
            "ORDER BY A.ChatRoomName ASC;")
        if roomwxid:
            sql = sql.replace("ORDER BY A.ChatRoomName ASC;",
                              f"and A.ChatRoomName LIKE '%{roomwxid}%' "
                              "ORDER BY A.ChatRoomName ASC;")
        result = self.execute_sql(sql)
        if not result:
            return []
        room_datas = []
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            ChatRoomName, UserNameList, DisplayNameList, RoomData, Announcement, AnnouncementEditor = row
            UserNameList = UserNameList.split("^G")
            DisplayNameList = DisplayNameList.split("^G")
            RoomData = self.ChatRoom_RoomData(RoomData)
            wxid2remark = {}
            if RoomData:
                rd = []
                for k, v in RoomData.items():
                    if isinstance(v, list):
                        rd += v
                for i in rd:
                    try:
                        if isinstance(i, dict) and isinstance(i.get('1'),str) and i.get('2'):
                            wxid2remark[i['1']] = i["2"]
                    except Exception as e:
                        logging.error(f"wxid2remark: ChatRoomName:{ChatRoomName}, {i} error:{e}")
            rooms.append(
                {"ChatRoomName": ChatRoomName, "UserNameList": UserNameList, "DisplayNameList": DisplayNameList,
                 "Announcement": Announcement, "AnnouncementEditor": AnnouncementEditor, "wxid2remark": wxid2remark})
        return rooms
