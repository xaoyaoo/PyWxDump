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
        self.MSG_exist = self.Msg_tables_exist()
        self.Micro_exist = self.Micro_tables_exist()
        self.Media_exist = self.Media_tables_exist()
        self.OpenIMContact_exist = self.OpenIMContact_tables_exist()
        self.PublicMsg_exist = self.PublicMSG_tables_exist()
        self.OpenIMMedia_exist = self.OpenIMMedia_tables_exist()
        self.Favorite_exist = self.Favorite_tables_exist()

        if self.MSG_exist:  # 添加索引
            self.Msg_add_index()
        if self.PublicMsg_exist:  # 添加索引
            self.PublicMsg_add_index()
        if self.Micro_exist:  # 添加索引
            self.Micro_add_index()

    def get_user(self, word=None, wxids=None, labels=None):
        """
        获取联系人列表
        """
        users = self.get_user_list(word=word, wxids=wxids, label_ids=labels) if self.Micro_exist else {}
        if self.OpenIMContact_exist: users.update(self.get_im_user_list(word=word, wxids=wxids))
        return users
