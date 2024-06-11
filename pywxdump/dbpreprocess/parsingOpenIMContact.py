# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parsingOpenIMContact.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/16
# -------------------------------------------------------------------------------
from .dbbase import DatabaseBase


class ParsingOpenIMContact(DatabaseBase):
    _class_name = "OpenIMContact"

    def __init__(self, db_path):
        super().__init__(db_path)

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
        sql = ("SELECT A.UserName, A.NickName, A.Remark,A.BigHeadImgUrl "
               "FROM OpenIMContact A "
               f"WHERE A.UserName in ({wxid}) "
               "ORDER BY NickName ASC;")

        result = self.execute_sql(sql)
        if not result:
            return {}
        users = {}
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            username, nickname, remark, headImgUrl = row
            users[username] = {"wxid": username, "nickname": nickname, "remark": remark, "account": "", "describe": "",
                               "headImgUrl": headImgUrl, "LabelIDList": ()}
        return users

    def user_list(self, word=None):
        """
        获取联系人列表
        :param MicroMsg_db_path: MicroMsg.db 文件路径
        :return: 联系人列表
        """
        sql = ("SELECT A.UserName, A.NickName, A.Remark,A.BigHeadImgUrl FROM OpenIMContact A "
               "ORDER BY NickName ASC;")
        if word:
            sql = sql.replace("ORDER BY NickName ASC;",
                              f"where "
                              f"UserName LIKE '%{word}%' "
                              f"OR NickName LIKE '%{word}%' "
                              f"OR Remark LIKE '%{word}%' "
                              "ORDER BY NickName ASC;")
        result = self.execute_sql(sql)
        if not result:
            return []

        users = []
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            username, nickname, remark, headImgUrl = row
            users.append(
                {"wxid": username, "nickname": nickname, "remark": remark, "account": "", "describe": "",
                 "headImgUrl": headImgUrl, "LabelIDList": ()})
        return users
