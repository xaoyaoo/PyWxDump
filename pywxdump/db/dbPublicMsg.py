# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         PublicMsg.py
# Description:  负责处理公众号数据库信息
# Author:       xaoyaoo
# Date:         2024/07/03
# -------------------------------------------------------------------------------
from .dbMSG import MsgHandler
from .utils import db_error


class PublicMsgHandler(MsgHandler):
    _class_name = "PublicMSG"
    PublicMSG_required_tables = ["PublicMsg"]

    def PublicMsg_add_index(self):
        """
        添加索引,加快查询速度
        """
        # 检查是否存在索引
        if not self.tables_exist("PublicMsg"):
            return
        sql = "CREATE INDEX IF NOT EXISTS idx_PublicMsg_StrTalker ON PublicMsg(StrTalker);"
        self.execute(sql)
        sql = "CREATE INDEX IF NOT EXISTS idx_PublicMsg_CreateTime ON PublicMsg(CreateTime);"
        self.execute(sql)
        sql = "CREATE INDEX IF NOT EXISTS idx_PublicMsg_StrTalker_CreateTime ON PublicMsg(StrTalker, CreateTime);"
        self.execute(sql)

    @db_error
    def get_plc_msg_count(self, wxids: list = ""):
        """
        获取聊天记录数量,根据wxid获取单个联系人的聊天记录数量，不传wxid则获取所有联系人的聊天记录数量
        :param wxids: wxid list
        :return: 聊天记录数量列表 {wxid: chat_count}
        """
        if not self.tables_exist("PublicMsg"):
            return {}
        if isinstance(wxids, str) and wxids:
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
    def get_plc_msg_list(self, wxids: list or str = "", start_index=0, page_size=500, msg_type: str = "",
                         msg_sub_type: str = "", start_createtime=None, end_createtime=None, my_talker="我"):
        """
        获取聊天记录列表
        :param wxids: [wxid]
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
        if not self.tables_exist("PublicMsg"):
            return [], []

        if isinstance(wxids, str) and wxids:
            wxids = [wxids]
        param = ()
        sql_wxid, param = (f"AND StrTalker in ({', '.join('?' for _ in wxids)}) ",
                           param + tuple(wxids)) if wxids else ("", param)
        sql_type, param = ("AND Type=? ", param + (msg_type,)) if msg_type else ("", param)
        sql_sub_type, param = ("AND SubType=? ", param + (msg_sub_type,)) if msg_type and msg_sub_type else ("", param)
        sql_start_createtime, param = ("AND CreateTime>=? ", param + (start_createtime,)) if start_createtime else (
            "", param)
        sql_end_createtime, param = ("AND CreateTime<=? ", param + (end_createtime,)) if end_createtime else ("", param)

        sql = (
            "SELECT localId,TalkerId,MsgSvrID,Type,SubType,CreateTime,IsSender,Sequence,StatusEx,FlagEx,Status,"
            "MsgSequence,StrContent,MsgServerSeq,StrTalker,DisplayContent,Reserved0,Reserved1,Reserved3,"
            "Reserved4,Reserved5,Reserved6,CompressContent,BytesExtra,BytesTrans,Reserved2,"
            "ROW_NUMBER() OVER (ORDER BY CreateTime ASC) AS id "
            "FROM PublicMsg WHERE 1=1 "
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

        result_data = (self.get_msg_detail(row, my_talker=my_talker) for row in result)
        rdata = list(result_data)  # 转为列表
        wxid_list = {d['talker'] for d in rdata}  # 创建一个无重复的 wxid 列表

        return rdata, list(wxid_list)
