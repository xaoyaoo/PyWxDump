# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         exportCSV.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/20
# -------------------------------------------------------------------------------
import json
import os
from pywxdump.db import DBHandler


def export_json(wxid, outpath, db_config, my_wxid="我", indent=4):
    if not os.path.exists(outpath):
        outpath = os.path.join(os.getcwd(), "export" + os.sep + wxid)
        if not os.path.exists(outpath):
            os.makedirs(outpath)

    db = DBHandler(db_config, my_wxid)

    count = db.get_msgs_count(wxid)
    chatCount = count.get(wxid, 0)
    if chatCount == 0:
        return False, "没有聊天记录"
    users = {}
    page_size = chatCount + 1
    for i in range(0, chatCount, page_size):
        start_index = i
        data, users_t = db.get_msgs(wxid, start_index, page_size)
        users.update(users_t)
        if len(data) == 0:
            return False, "没有聊天记录"

        save_path = os.path.join(outpath, f"{wxid}_{i}_{i + page_size}.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    with open(os.path.join(outpath, "users.json"), "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=indent)
    return True, f"导出成功: {outpath}"


if __name__ == '__main__':
    pass
