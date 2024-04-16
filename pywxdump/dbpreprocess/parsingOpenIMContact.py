# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parsingOpenIMContact.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/16
# -------------------------------------------------------------------------------
from .dbbase import DatabaseBase


class ParsingOpenIMContact(DatabaseBase):
    def __init__(self, db_path):
        super().__init__(db_path)

    def user_list(self):
        """
        获取联系人列表
        :param MicroMsg_db_path: MicroMsg.db 文件路径
        :return: 联系人列表
        """
        users = []
        sql = ("SELECT A.UserName, A.NickName, A.Remark,A.BigHeadImgUrl FROM OpenIMContact A "
               "ORDER BY NickName ASC;")
        result = self.execute_sql(sql)
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            username, nickname, remark, headImgUrl = row
            users.append(
                {"wxid": username, "nickname": nickname, "remark": remark, "account": "", "describe": "",
                 "headImgUrl": headImgUrl})
        return users
