# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         exportCSV.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/20
# -------------------------------------------------------------------------------
import json
import os
from ..parsingMSG import ParsingMSG


def export_json(wxid, outpath, msg_path):
    if not os.path.exists(outpath):
        outpath = os.path.join(os.getcwd(), "export" + os.sep + wxid)
        if not os.path.exists(outpath):
            os.makedirs(outpath)

    pmsg = ParsingMSG(msg_path)

    count = pmsg.msg_count(wxid)
    chatCount = count.get(wxid, 0)
    if chatCount == 0:
        return False, "没有聊天记录"

    page_size = chatCount + 1
    for i in range(0, chatCount, page_size):
        start_index = i
        data, wxid_list = pmsg.msg_list(wxid, start_index, page_size)
        if len(data) == 0:
            return False, "没有聊天记录"
        save_path = os.path.join(outpath, f"{wxid}_{i}_{i + page_size}.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    return True, f"导出成功: {outpath}"


if __name__ == '__main__':
    pass
