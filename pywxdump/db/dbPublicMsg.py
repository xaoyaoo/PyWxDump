# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parsingPublicMsg.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/07/03
# -------------------------------------------------------------------------------

# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parsingMSG.py
# Description:
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
import json
import os
import re
from typing import Union, Tuple

import pandas as pd

from .dbbase import DatabaseBase
from .dbMSG import MsgHandler
from .utils import get_md5, name2typeid, typeid2name, type_converter, timestamp2str, xml2dict, match_BytesExtra, \
    db_error
import lz4.block
import blackboxprotobuf


class PublicMsgHandler(MsgHandler):
    _class_name = "PublicMSG"
    PublicMSG_required_tables = ["PublicMsg"]

    @db_error
    def PublicMSG_tables_exist(self):
        """
        判断该类所需要的表是否存在
        """
        return self.check_tables_exist(self.PublicMSG_required_tables)

    def PublicMsg_add_index(self):
        """
        添加索引,加快查询速度
        """
        # 检查是否存在索引
        sql = "CREATE INDEX IF NOT EXISTS idx_PublicMsg_StrTalker ON MSG(StrTalker);"
        self.execute(sql)
        sql = "CREATE INDEX IF NOT EXISTS idx_PublicMsg_CreateTime ON MSG(CreateTime);"
        self.execute(sql)
        sql = "CREATE INDEX IF NOT EXISTS idx_PublicMsg_StrTalker_CreateTime ON MSG(StrTalker, CreateTime);"
        self.execute(sql)

    @db_error
    def get_plc_msg_count(self, wxids: list = ""):
        """
        获取聊天记录数量,根据wxid获取单个联系人的聊天记录数量，不传wxid则获取所有联系人的聊天记录数量
        :param wxids: wxid list
        :return: 聊天记录数量列表 {wxid: chat_count}
        """
        if isinstance(wxids, str):
            wxids = [wxids]
        if wxids:
            wxids = "('" + "','".join(wxids) + "')"
            sql = f"SELECT StrTalker, COUNT(*) FROM PublicMsg WHERE StrTalker IN {wxids} GROUP BY StrTalker ORDER BY COUNT(*) DESC;"
        else:
            sql = f"SELECT StrTalker, COUNT(*) FROM PublicMsg GROUP BY StrTalker ORDER BY COUNT(*) DESC;"
        sql_total = f"SELECT COUNT(*) FROM MSG;"

        result = self.execute(sql)
        total_ret = self.execute(sql_total)

        if not result:
            return {}
        total = 0
        if total_ret and len(total_ret) > 0:
            total = total_ret[0][0]

        msg_count = {"total": total}
        msg_count.update({row[0]: row[1] for row in result})
        return msg_count

    @db_error
    def get_plc_msg_list(self, wxid="", start_index=0, page_size=500, msg_type: str = "", msg_sub_type: str = "",
                         start_createtime=None, end_createtime=None):
        sql_base = ("SELECT localId,TalkerId,MsgSvrID,Type,SubType,CreateTime,IsSender,Sequence,StatusEx,FlagEx,Status,"
                    "MsgSequence,StrContent,MsgServerSeq,StrTalker,DisplayContent,Reserved0,Reserved1,Reserved3,"
                    "Reserved4,Reserved5,Reserved6,CompressContent,BytesExtra,BytesTrans,Reserved2,"
                    "ROW_NUMBER() OVER (ORDER BY CreateTime ASC) AS id "
                    "FROM PublicMsg ")

        param = ()
        sql_wxid, param = ("AND StrTalker=? ", param + (wxid,)) if wxid else ("", param)
        sql_type, param = ("AND Type=? ", param + (msg_type,)) if msg_type else ("", param)
        sql_sub_type, param = ("AND SubType=? ", param + (msg_sub_type,)) if msg_type and msg_sub_type else ("", param)
        sql_start_createtime, param = ("AND CreateTime>=? ", param + (start_createtime,)) if start_createtime else (
            "", param)
        sql_end_createtime, param = ("AND CreateTime<=? ", param + (end_createtime,)) if end_createtime else ("", param)

        sql = (
            f"{sql_base} WHERE 1=1 "
            f"{sql_wxid}"
            f"{sql_type}"
            f"{sql_sub_type}"
            f"{sql_start_createtime}"
            f"{sql_end_createtime}"
            f"ORDER BY CreateTime ASC LIMIT ?,?"
        )
        param = param + (start_index, page_size)
        result = self.execute(sql, param)
        if not result:
            return [], []

        result_data = (self.get_msg_detail(row) for row in result)
        rdata = list(result_data)  # 转为列表
        wxid_list = {d['talker'] for d in rdata}  # 创建一个无重复的 wxid 列表

        return rdata, list(wxid_list)
