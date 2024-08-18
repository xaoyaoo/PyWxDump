# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         __init__.py
# Description:  db
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
from .utils import download_file, dat2img

from .dbFavorite import FavoriteHandler
from .dbMSG import MsgHandler
from .dbMicro import MicroHandler
from .dbMedia import MediaHandler
from .dbOpenIMContact import OpenIMContactHandler
from .dbPublicMsg import PublicMsgHandler
from .dbOpenIMMedia import OpenIMMediaHandler
from .dbSns import SnsHandler


class DBHandler(MicroHandler, MediaHandler, OpenIMContactHandler, PublicMsgHandler, OpenIMMediaHandler,
                FavoriteHandler, SnsHandler):
    _class_name = "DBHandler"

    def __init__(self, db_config, my_wxid, *args, **kwargs):
        self.config = db_config
        self.my_wxid = my_wxid

        super().__init__(self.config)
        # 加速查询索引
        self.Micro_add_index()
        self.Msg_add_index()
        self.PublicMsg_add_index()
        self.Media_add_index()

    def get_user(self, word=None, wxids=None, labels=None):
        """
        获取联系人列表
        :param word: 搜索关键字
        :param wxids: wxid列表
        :param labels: 标签列表
        :return: 联系人dict {wxid: {}}
        """
        users = self.get_user_list(word=word, wxids=wxids, label_ids=labels)
        users.update(self.get_im_user_list(word=word, wxids=wxids))
        return users

    def get_msgs(self, wxids: list or str = "", start_index=0, page_size=500, msg_type: str = "",
                 msg_sub_type: str = "", start_createtime=None, end_createtime=None):
        """
        获取聊天记录列表
        :param wxids:[ wxid]
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
        msgs0, wxid_list0 = self.get_msg_list(wxids=wxids, start_index=start_index, page_size=page_size,
                                              msg_type=msg_type,
                                              msg_sub_type=msg_sub_type, start_createtime=start_createtime,
                                              end_createtime=end_createtime, my_talker=self.my_wxid)
        msgs1, wxid_list1 = self.get_plc_msg_list(wxids=wxids, start_index=start_index, page_size=page_size,
                                                  msg_type=msg_type,
                                                  msg_sub_type=msg_sub_type, start_createtime=start_createtime,
                                                  end_createtime=end_createtime, my_talker=self.my_wxid)
        msgs = msgs0 + msgs1
        wxid_list = wxid_list0 + wxid_list1

        users = self.get_user(wxids=wxid_list)
        return msgs, users

    def get_msgs_count(self, wxids: list = ""):
        chat_count = self.get_m_msg_count(wxids)
        chat_count1 = self.get_plc_msg_count(wxids)
        # 合并两个字典，相同key，则将value相加
        count = {k: chat_count.get(k, 0) + chat_count1.get(k, 0) for k in
                 list(set(list(chat_count.keys()) + list(chat_count1.keys())))}
        return count


__all__ = ["DBHandler", "FavoriteHandler", "MsgHandler", "MicroHandler", "MediaHandler",
           "OpenIMContactHandler", "PublicMsgHandler", "OpenIMMediaHandler", "SnsHandler"]
