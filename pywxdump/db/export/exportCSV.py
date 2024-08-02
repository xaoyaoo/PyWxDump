# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         exportCSV.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/20
# -------------------------------------------------------------------------------
import csv
import json
import os
from ..dbMSG import MsgHandler


def export_csv(wxid, outpath, db_config, page_size=5000):
    if not os.path.exists(outpath):
        outpath = os.path.join(os.getcwd(), "export" + os.sep + wxid)
        if not os.path.exists(outpath):
            os.makedirs(outpath)

    pmsg = MsgHandler(db_config)

    count = pmsg.get_msg_count(wxid)
    chatCount = count.get(wxid, 0)
    if chatCount == 0:
        return False, "没有聊天记录"

    if page_size > chatCount:
        page_size = chatCount + 1

    for i in range(0, chatCount, page_size):
        start_index = i
        data, wxid_list = pmsg.get_msg_list(wxid, start_index, page_size)

        if len(data) == 0:
            return False, "没有聊天记录"

        save_path = os.path.join(outpath, f"{wxid}_{i}_{i + page_size}.csv")

        with open(save_path, "w", encoding="utf-8", newline='') as f:
            csv_writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)

            csv_writer.writerow(["id", "MsgSvrID", "type_name", "is_sender", "talker", "room_name", "msg", "src",
                                 "CreateTime"])
            for row in data:
                id = row.get("id", "")
                MsgSvrID = row.get("MsgSvrID", "")
                type_name = row.get("type_name", "")
                is_sender = row.get("is_sender", "")
                talker = row.get("talker", "")
                room_name = row.get("room_name", "")
                msg = row.get("msg", "")
                src = row.get("src", "")
                CreateTime = row.get("CreateTime", "")
                csv_writer.writerow([id, MsgSvrID, type_name, is_sender, talker, room_name, msg, src, CreateTime])

    return True, f"导出成功: {outpath}"


if __name__ == '__main__':
    pass
