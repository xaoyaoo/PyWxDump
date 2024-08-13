# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         exportCSV.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/20
# -------------------------------------------------------------------------------
import json
import os
from ..__init__ import DBHandler


def export_html(wxid, outpath, db_config, my_wxid="我"):
    if not os.path.exists(outpath):
        outpath = os.path.join(os.getcwd(), "export" + os.sep + wxid)
        if not os.path.exists(outpath):
            os.makedirs(outpath)

    db = DBHandler(db_config, my_wxid)

    count = db.get_msgs_count(wxid)
    chatCount = count.get(wxid, 0)
    if chatCount == 0:
        return False, "没有聊天记录"

    msgs, users = db.get_msgs(wxid, 0, chatCount + 1)
    if len(msgs) == 0:
        return False, "没有聊天记录"

    data_js = (
        "localStorage.setItem('isUseLocalData', 't')  //  't' : 'f' \n"
        f"const local_msg_count = {chatCount}\n"
        f"const local_mywxid = '{my_wxid}' \n"
        f"const local_user_list = {json.dumps(users, ensure_ascii=False, indent=None )} \n"
        f"const local_msg_list = {json.dumps(msgs, ensure_ascii=False, indent=None )} \n"
    )

    save_path = os.path.join(outpath, f"data.js")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(data_js)

    return True, f"导出成功: {outpath}"


if __name__ == '__main__':
    pass
