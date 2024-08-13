# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         __init__.py.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
import pandas as pd

from .utils import download_file, dat2img

from .dbFavorite import FavoriteHandler
from .dbMSG import MsgHandler
from .dbMicro import MicroHandler
from .dbMedia import MediaHandler
from .dbOpenIMContact import OpenIMContactHandler
from .dbPublicMsg import PublicMsgHandler
from .dbOpenIMMedia import OpenIMMediaHandler

from .export.exportCSV import export_csv
from .export.exportJSON import export_json


class DBHandler(MicroHandler, MediaHandler, OpenIMContactHandler, PublicMsgHandler, OpenIMMediaHandler,
                FavoriteHandler):
    _class_name = "DBHandler"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Micro_add_index()
        self.Msg_add_index()
        self.PublicMsg_add_index()

    def get_user(self, word=None, wxids=None, labels=None):
        """
        获取联系人列表
        """
        users = self.get_user_list(word=word, wxids=wxids, label_ids=labels)
        users.update(self.get_im_user_list(word=word, wxids=wxids))
        return users

    def get_msgs(self, wxid="", start_index=0, page_size=500, msg_type: str = "", msg_sub_type: str = "",
                 start_createtime=None, end_createtime=None):
        """
        获取聊天记录列表
        :param wxid: wxid
        :param start_index: 起始索引
        :param page_size: 页大小
        :param msg_type: 消息类型
        :param msg_sub_type: 消息子类型
        :param start_createtime: 开始时间
        :param end_createtime: 结束时间
        :return: 聊天记录列表 {"id": _id, "MsgSvrID": str(MsgSvrID), "type_name": type_name, "is_sender": IsSender,
                    "talker": talker, "room_name": StrTalker, "msg": msg, "src": src, "extra": {},
                    "CreateTime": CreateTime, }
        """
        msgs0, wxid_list0 = self.get_msg_list(wxid=wxid, start_index=start_index, page_size=page_size,
                                              msg_type=msg_type,
                                              msg_sub_type=msg_sub_type, start_createtime=start_createtime,
                                              end_createtime=end_createtime)
        msgs1, wxid_list1 = self.get_plc_msg_list(wxid=wxid, start_index=start_index, page_size=page_size,
                                                  msg_type=msg_type,
                                                  msg_sub_type=msg_sub_type, start_createtime=start_createtime,
                                                  end_createtime=end_createtime)
        msgs = msgs0 + msgs1
        wxid_list = wxid_list0 + wxid_list1
        return msgs, wxid_list
