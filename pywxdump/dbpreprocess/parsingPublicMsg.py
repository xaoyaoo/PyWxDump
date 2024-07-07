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
from .parsingMSG import ParsingMSG
from .utils import get_md5, name2typeid, typeid2name, type_converter, timestamp2str, xml2dict, match_BytesExtra
import lz4.block
import blackboxprotobuf


class ParsingPublicMsg(ParsingMSG):
    _class_name = "PublicMSG"

    def msg_count(self, wxid: str = ""):
        """
        获取聊天记录数量,根据wxid获取单个联系人的聊天记录数量，不传wxid则获取所有联系人的聊天记录数量
        :param MSG_db_path: MSG.db 文件路径
        :return: 聊天记录数量列表 {wxid: chat_count}
        """
        if wxid:
            sql = f"SELECT StrTalker, COUNT(*) FROM PublicMsg WHERE StrTalker='{wxid}';"
        else:
            sql = f"SELECT StrTalker, COUNT(*) FROM PublicMsg GROUP BY StrTalker ORDER BY COUNT(*) DESC;"

        result = self.execute_sql(sql)
        if not result:
            return {}
        df = pd.DataFrame(result, columns=["wxid", "msg_count"])
        # # 排序
        df = df.sort_values(by="msg_count", ascending=False)
        # chat_counts ： {wxid: chat_count}
        chat_counts = df.set_index("wxid").to_dict()["msg_count"]
        return chat_counts

    def msg_count_total(self):
        """
        获取聊天记录总数
        :return: 聊天记录总数
        """
        sql = "SELECT COUNT(*) FROM PublicMsg;"
        result = self.execute_sql(sql)
        if result and len(result) > 0:
            chat_counts = result[0][0]
            return chat_counts
        return 0


    def msg_list(self, wxid="", start_index=0, page_size=500, msg_type: str = ""):
        sql = (
            "SELECT localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType, CreateTime, MsgSvrID, "
            "DisplayContent, CompressContent, BytesExtra, ROW_NUMBER() OVER (ORDER BY CreateTime ASC) AS id "
            "FROM PublicMsg WHERE 1==1 "
            "ORDER BY CreateTime ASC LIMIT ?, ?"
        )
        params = [start_index, page_size]
        if msg_type:
            sql = sql.replace("ORDER BY CreateTime ASC LIMIT ?, ?",
                              f"AND Type=? ORDER BY CreateTime ASC LIMIT ?,?")
            params = [msg_type] + params

        if wxid:
            sql = sql.replace("WHERE 1==1", f"WHERE StrTalker=? ")
            params = [wxid] + params
        params = tuple(params)
        result1 = self.execute_sql(sql, params)
        if not result1:
            return [], []
        data = []
        wxid_list = []
        for row in result1:
            tmpdata = self.msg_detail(row)
            wxid_list.append(tmpdata["talker"])
            data.append(tmpdata)
        wxid_list = list(set(wxid_list))
        return data, wxid_list
