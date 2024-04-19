# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         __init__.py.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
import pandas as pd

from .parsingMSG import ParsingMSG
from .parsingMicroMsg import ParsingMicroMsg
from .parsingMediaMSG import ParsingMediaMSG
from .parsingOpenIMContact import ParsingOpenIMContact
from .utils import download_file


def get_user_list(MicroMsg_db_path, OpenIMContact_db_path=None, word=None):
    """
    获取联系人列表
    :param MicroMsg_db_path: MicroMsg.db 文件路径
    :return: 联系人列表
    """
    # 连接 MicroMsg.db 数据库，并执行查询
    if not MicroMsg_db_path:
        return []
    parsing_micromsg = ParsingMicroMsg(MicroMsg_db_path)
    users = parsing_micromsg.user_list(word=word)
    # 如果有 OpenIMContact.db 文件，获取 OpenIMContact.db 中的联系人信息
    if OpenIMContact_db_path:
        parsing_openimcontact = ParsingOpenIMContact(OpenIMContact_db_path)
        users += parsing_openimcontact.user_list(word=word)
    # 去重
    users = [dict(t) for t in {tuple(d.items()) for d in users}]
    return users


def get_recent_user_list(MicroMsg_db_path, OpenIMContact_db_path=None,limit=200):
    """
    获取联系人列表
    :param MicroMsg_db_path: MicroMsg.db 文件路径
    :return: 联系人列表
    """
    # 连接 MicroMsg.db 数据库，并执行查询
    if not MicroMsg_db_path:
        return []
    parsing_micromsg = ParsingMicroMsg(MicroMsg_db_path)
    recent_users = parsing_micromsg.recent_chat_wxid()  # [{"wxid": username, "LastReadedCreateTime": LastReadedCreateTime, "LastReadedSvrId": LastReadedSvrId},]
    recent_users = pd.DataFrame(recent_users)
    recent_users = recent_users.sort_values(by="LastReadedCreateTime", ascending=False)
    recent_users = recent_users.drop_duplicates(subset=["wxid"], keep="first").head(limit)

    users = get_user_list(MicroMsg_db_path, OpenIMContact_db_path)
    users = pd.DataFrame(users)

    users = pd.merge(users, recent_users, on="wxid", how="right")
    # users = users.drop_duplicates(subset=["wxid"], keep="last")  # 保留最新的
    users = users.sort_values(by="LastReadedCreateTime", ascending=False)  # 按照最新的排序
    users = users.drop_duplicates(subset=["wxid"], keep="first")  # 保留最新的
    users = users.fillna("")
    users = users.to_dict(orient="records")
    return users


def wxid2userinfo(MicroMsg_db_path, OpenIMContact_db_path, wxid):
    """
    获取联系人信息
    :param MicroMsg_db_path: MicroMsg.db 文件路径
    :param wxid: 微信id
    :return: 联系人信息 {wxid: {wxid: wxid, nickname: nickname, remark: remark, account: account, describe: describe, headImgUrl: headImgUrl}}
    """
    # 连接 MicroMsg.db 数据库，并执行查询
    parsing_micromsg = ParsingMicroMsg(MicroMsg_db_path)
    users = parsing_micromsg.wxid2userinfo(wxid)
    # {'wxid_uw8ruinee7zq12': {'wxid': 'wxid_uw8ruinee7zq12', 'nickname': '2021年', 'remark': '于浩', 'account': 'yh13327404424', 'describe': '', 'headImgUrl': 'https://wx.qlogo.cn/mmhead/ver_1/LLibM2qUys7nBt9Hl8uuTQkn9ILFicoImlt2616ZNGoIvRbA8VmJ0Vibhd3V96JFfxQ25Tj1nRWTsXYDdH3z2FAQkQDXSnjS5PBuSraey4ZnoooOkEu2e3DjXbJaJJXKUib1/0'}}
    # 如果有 OpenIMContact.db 文件，获取 OpenIMContact.db 中的联系人信息
    if OpenIMContact_db_path:
        parsing_openimcontact = ParsingOpenIMContact(OpenIMContact_db_path)
        users.update(parsing_openimcontact.wxid2userinfo(wxid))
    return users
