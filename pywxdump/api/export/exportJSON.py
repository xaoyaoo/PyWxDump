# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         exportCSV.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/20
# -------------------------------------------------------------------------------
import datetime
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


def export_json_mini(wxid, outpath, db_config, my_wxid="我", indent=4):
    # 确保输出目录存在
    if not os.path.exists(outpath):
        outpath = os.path.join(os.getcwd(), "export_mini" + os.sep + wxid)
        os.makedirs(outpath, exist_ok=True)

    db = DBHandler(db_config, my_wxid)

    # 获取消息总数
    count = db.get_msgs_count(wxid)
    chatCount = count.get(wxid, 0)
    if chatCount == 0:
        return False, "没有聊天记录"

    users = {}
    page_size = chatCount + 1  # 保持与原函数一致的分页逻辑

    for i in range(0, chatCount, page_size):
        start_index = i
        data, users_t = db.get_msgs(wxid, start_index, page_size)
        users.update(users_t)  # 合并用户信息

        if not data:
            continue

        # 构建简化数据
        mini_data = []
        for msg in data:
            # 获取昵称（优先用备注，没有则用昵称，最后用wxid）
            user_info = users.get(msg.get("talker"), {})
            nickname = user_info.get("remark") or user_info.get("nickname") or msg.get("talker")

            mini_msg = {
                "nickname": nickname,
                "message": msg.get("msg", ""),
                "time": msg.get("CreateTime", "")
            }
            mini_data.append(mini_msg)

        # 保存简化后的文件
        save_path = os.path.join(outpath, f"{wxid}_mini_{i}_{i + page_size}.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(mini_data, f, ensure_ascii=False, indent=indent)

    return True, f"简化版导出成功: {outpath}"


def export_json_mini_time_limit(wxid, outpath, db_config, my_wxid="我",
                     start_createtime=None, end_createtime=None, indent=4):
    """
    带时间过滤的简化版聊天记录导出

    :param start_createtime: 开始时间（格式：2025-4-30 16:55:01）
    :param end_createtime: 结束时间（格式：2025-4-30 16:55:01）
    """
    # 创建输出目录
    if not os.path.exists(outpath):
        outpath = os.path.join(os.getcwd(), "export_mini" + os.sep + wxid)
        os.makedirs(outpath, exist_ok=True)

    # 初始化数据库连接
    db = DBHandler(db_config, my_wxid)

    # 时间格式转换
    def str_to_timestamp(time_str):
        if not time_str:
            return None
        try:
            dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())
        except ValueError:
            raise ValueError(f"无效时间格式: {time_str}，示例: 2025-04-30 16:55:01")

    start_ts = str_to_timestamp(start_createtime)
    end_ts = str_to_timestamp(end_createtime)

    # 获取消息数据（带时间过滤）
    all_data = []
    users = {}
    page_size = 5000  # 每次获取5000条
    start_index = 0

    while True:
        # 获取分页数据（自动包含时间过滤条件）
        data, users_t = db.get_msgs(
            wxid,
            start_index=start_index,
            page_size=page_size,
            start_createtime=start_ts,
            end_createtime=end_ts
        )

        if not data:
            break

        all_data.extend(data)
        users.update(users_t)
        start_index += page_size

    if not all_data:
        return False, "指定时间段内没有聊天记录"

    # 构建简化数据结构
    mini_data = []
    for msg in all_data:
        talker = msg.get("talker")
        user_info = users.get(talker, {})

        mini_msg = {
            "sender": user_info.get("remark") or user_info.get("nickname") or talker,
            "content": msg.get("msg", ""),
            "timestamp": msg.get("CreateTime")
        }
        mini_data.append(mini_msg)

    # 生成带时间范围的文件名
    time_suffix = ""
    if start_createtime or end_createtime:
        start_part = start_createtime.replace(" ", "_").replace(":", "-") if start_createtime else "all"
        end_part = end_createtime.replace(" ", "_").replace(":", "-") if end_createtime else "now"
        time_suffix = f"_{start_part}_to_{end_part}"
    filename = f"{wxid}_mini{time_suffix}.json"
    save_path = os.path.join(outpath, filename)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(mini_data, f, ensure_ascii=False, indent=indent)

    return True, f"导出成功: {save_path}", filename



if __name__ == '__main__':
    pass
