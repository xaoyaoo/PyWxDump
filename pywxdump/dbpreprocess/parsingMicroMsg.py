# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parsingMicroMsg.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
from .dbbase import DatabaseBase


class ParsingMicroMsg(DatabaseBase):
    def __init__(self, db_path):
        super().__init__(db_path)

    def wxid2userinfo(self, wx_id):
        """
        获取单个联系人信息
        :param wx_id: 微信id
        :return: 联系人信息
        """
        # 获取username是wx_id的用户
        sql = ("SELECT A.UserName, A.NickName, A.Remark,A.Alias,A.Reserved6,B.bigHeadImgUrl "
               "FROM Contact A,ContactHeadImgUrl B "
               f"WHERE A.UserName = '{wx_id}' AND A.UserName = B.usrName "
               "ORDER BY NickName ASC;")
        result = self.execute_sql(sql)
        if not result:
            return None
        result = result[0]
        return {"wxid": result[0], "nickname": result[1], "remark": result[2], "account": result[3],
                "describe": result[4], "headImgUrl": result[5]}

    def user_list(self):
        """
        获取联系人列表
        :param MicroMsg_db_path: MicroMsg.db 文件路径
        :return: 联系人列表
        """
        users = []
        sql = ("SELECT A.UserName, A.NickName, A.Remark,A.Alias,A.Reserved6,B.bigHeadImgUrl "
               "FROM Contact A,ContactHeadImgUrl B "
               "where UserName==usrName "
               "ORDER BY NickName ASC;")

        result = self.execute_sql(sql)
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            username, nickname, remark, Alias, describe, headImgUrl = row
            users.append(
                {"wxid": username, "nickname": nickname, "remark": remark, "account": Alias,
                 "describe": describe, "headImgUrl": headImgUrl})
        return users

    def chatroom_list(self):
        """
        获取群聊列表
        :param MicroMsg_db_path: MicroMsg.db 文件路径
        :return: 群聊列表
        """
        rooms = []
        # 连接 MicroMsg.db 数据库，并执行查询
        sql = ("SELECT A.ChatRoomName,A.UserNameList, A.DisplayNameList, B.Announcement,B.AnnouncementEditor "
               "FROM ChatRoom A,ChatRoomInfo B "
               "where A.ChatRoomName==B.ChatRoomName "
               "ORDER BY A.ChatRoomName ASC;")
        result = self.execute_sql(sql)
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            ChatRoomName, UserNameList, DisplayNameList, Announcement, AnnouncementEditor = row
            UserNameList = UserNameList.split("^G")
            DisplayNameList = DisplayNameList.split("^G")
            rooms.append(
                {"ChatRoomName": ChatRoomName, "UserNameList": UserNameList, "DisplayNameList": DisplayNameList,
                 "Announcement": Announcement, "AnnouncementEditor": AnnouncementEditor})
        return rooms
