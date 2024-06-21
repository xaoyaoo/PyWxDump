# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parsingMicroMsg.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
import logging

from .dbbase import DatabaseBase
from .utils import timestamp2str, bytes2str

import blackboxprotobuf


class ParsingMicroMsg(DatabaseBase):
    _class_name = "MicroMsg"

    def __init__(self, db_path):
        super().__init__(db_path)

    def get_BytesExtra(self, BytesExtra):
        if BytesExtra is None or not isinstance(BytesExtra, bytes):
            return None
        try:
            deserialize_data, message_type = blackboxprotobuf.decode_message(BytesExtra)
            return deserialize_data
        except Exception as e:
            return None

    def get_ExtraBuf(self, ExtraBuf: bytes):
        """
        读取ExtraBuf（联系人表）
        :param ExtraBuf:
        :return:
        """
        if not ExtraBuf:
            return None
        try:
            buf_dict = {
                'DDF32683': '0', '74752C06': '性别[1男2女]', '88E28FCE': '2', '761A1D2D': '3', '0263A0CB': '4',
                '0451FF12': '5',
                '228C66A8': '6', '46CF10C4': '个性签名', 'A4D9024A': '国', 'E2EAA8D1': '省', '1D025BBF': '市',
                '4D6C4570': '11',
                'F917BCC0': '公司名称', '759378AD': '手机号', '4335DFDD': '14', 'DE4CDAEB': '15', 'A72BC20A': '16',
                '069FED52': '17',
                '9B0F4299': '18', '3D641E22': '19', '1249822C': '20', '4EB96D85': '企微属性', 'B4F73ACB': '22',
                '0959EB92': '23',
                '3CF4A315': '24', 'C9477AC60201E44CD0E8': '26', 'B7ACF0F5': '28', '57A7B5A8': '29',
                '81AE19B4': '朋友圈背景',
                '695F3170': '31', 'FB083DD9': '32', '0240E37F': '33', '315D02A3': '34', '7DEC0BC3': '35',
                '0E719F13': '备注图片',
                '16791C90': '37'
            }

            rdata = {}
            for buf_name in buf_dict:
                rdata_name = buf_dict[buf_name]
                buf_name = bytes.fromhex(buf_name)
                offset = ExtraBuf.find(buf_name)
                if offset == -1:
                    rdata[rdata_name] = ""
                    continue
                offset += len(buf_name)
                type_id = ExtraBuf[offset: offset + 1]
                offset += 1

                if type_id == b"\x04":
                    rdata[rdata_name] = int.from_bytes(ExtraBuf[offset: offset + 4], "little")

                elif type_id == b"\x18":
                    length = int.from_bytes(ExtraBuf[offset: offset + 4], "little")
                    rdata[rdata_name] = ExtraBuf[offset + 4: offset + 4 + length].decode("utf-16").rstrip("\x00")

                elif type_id == b"\x17":
                    length = int.from_bytes(ExtraBuf[offset: offset + 4], "little")
                    rdata[rdata_name] = ExtraBuf[offset + 4: offset + 4 + length].decode("utf-8").rstrip("\x00")

                elif type_id == b"\x05":
                    rdata[rdata_name] = f"0x{ExtraBuf[offset: offset + 8].hex()}"
            return rdata
        except Exception as e:
            print(f'解析错误:\n{e}')
            return None

    def ChatRoom_RoomData(self, RoomData):
        # 读取群聊数据,主要为 wxid，以及对应昵称
        if RoomData is None or not isinstance(RoomData, bytes):
            return None
        try:
            data = self.get_BytesExtra(RoomData)
            bytes2str(data)
            return data
        except Exception as e:
            return None

    def wxid2userinfo(self, wxid):
        """
        获取单个联系人信息
        :param wxid: 微信id,可以是单个id，也可以是id列表
        :return: 联系人信息
        """
        if isinstance(wxid, str):
            wxid = [wxid]
        elif isinstance(wxid, list):
            wxid = wxid
        else:
            return {}
        wxid = "','".join(wxid)
        wxid = f"'{wxid}'"
        # 获取username是wx_id的用户
        sql = ("SELECT A.UserName, A.NickName, A.Remark,A.Alias,A.Reserved6,B.bigHeadImgUrl,A.LabelIDList "
               "FROM Contact A,ContactHeadImgUrl B "
               f"WHERE A.UserName = B.usrName AND A.UserName in ({wxid}) "
               "ORDER BY NickName ASC;")
        result = self.execute_sql(sql)
        if not result:
            return {}
        users = {}
        for row in result:
            # 获取wxid,昵称，备注，描述，头像
            username, nickname, remark, Alias, describe, headImgUrl, LabelIDList = row
            LabelIDList = LabelIDList.split(",") if LabelIDList else []
            users[username] = {"wxid": username, "nickname": nickname, "remark": remark, "account": Alias,
                               "describe": describe, "headImgUrl": headImgUrl, "LabelIDList": tuple(LabelIDList)}
        return users

    def user_list(self, word=None):
        """
        获取联系人列表
        :param word 查询关键字，可以是用户名、昵称、备注、描述，允许拼音
        :return: 联系人列表
        """
        users = []
        sql = (
            "SELECT A.UserName, A.NickName, A.Remark,A.Alias,A.Reserved6,B.bigHeadImgUrl,A.LabelIDList "
            "FROM Contact A left join ContactHeadImgUrl B on A.UserName==B.usrName "
            "ORDER BY A.NickName DESC;")
        if word:
            sql = sql.replace("ORDER BY A.NickName DESC;",
                              f"where "
                              f"A.UserName LIKE '%{word}%' "
                              f"OR A.NickName LIKE '%{word}%' "
                              f"OR A.Remark LIKE '%{word}%' "
                              f"OR A.Alias LIKE '%{word}%' "
                              f"OR A.QuanPin LIKE LOWER('%{word}%') "
                              f"OR LOWER(A.PYInitial) LIKE LOWER('%{word}%') "
                              # f"OR A.Reserved6 LIKE '%{word}%' "
                              "ORDER BY A.NickName DESC;")
        result = self.execute_sql(sql)
        if not result:
            return []
        for row in result:
            # 获取wxid,昵称，备注，描述，头像,标签
            username, nickname, remark, Alias, describe, headImgUrl, LabelIDList = row
            LabelIDList = LabelIDList.split(",") if LabelIDList else []
            users.append(
                {"wxid": username, "nickname": nickname, "remark": remark, "account": Alias,
                 "describe": describe, "headImgUrl": headImgUrl if headImgUrl else "",
                 "LabelIDList": tuple(LabelIDList)})
        return users

    def user_list_by_label(self, label_id):
        """
        获取标签联系人列表
        :param label_id: 标签id
        :return: 标签联系人列表
        """
        users = []
        sql = (
            "SELECT A.UserName, A.NickName, A.Remark,A.Alias,A.Reserved6,B.bigHeadImgUrl,A.LabelIDList "
            "FROM Contact A left join ContactHeadImgUrl B on A.UserName==B.usrName "
            f"where A.LabelIDList LIKE '%{label_id}%' "
            "ORDER BY A.NickName DESC;")
        result = self.execute_sql(sql)
        if not result:
            return []
        for row in result:
            # 获取wxid,昵称，备注，描述，头像,标签
            username, nickname, remark, Alias, describe, headImgUrl, LabelIDList = row
            LabelIDList = LabelIDList.split(",") if LabelIDList else []
            users.append(
                {"wxid": username, "nickname": nickname, "remark": remark, "account": Alias,
                 "describe": describe, "headImgUrl": headImgUrl if headImgUrl else "",
                 "LabelIDList": tuple(LabelIDList)})
        return users

    def recent_chat_wxid(self):
        """
        获取最近聊天的联系人
        :return: 最近聊天的联系人
        """
        users = []
        sql = (
            "SELECT C.Username, C.LastReadedCreateTime,C.LastReadedSvrId "
            "FROM ChatInfo C "
            "ORDER BY C.LastReadedCreateTime DESC;")
        result = self.execute_sql(sql)
        if not result:
            return []
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            username, LastReadedCreateTime, LastReadedSvrId = row
            LastReadedCreateTime = timestamp2str(LastReadedCreateTime) if LastReadedCreateTime else None
            users.append(
                {"wxid": username, "LastReadedCreateTime": LastReadedCreateTime, "LastReadedSvrId": LastReadedSvrId})
        return users

    def chatroom_list(self, roomwxid=None):
        """
        获取群聊列表
        :param MicroMsg_db_path: MicroMsg.db 文件路径
        :return: 群聊列表
        """
        rooms = []
        # 连接 MicroMsg.db 数据库，并执行查询
        sql = (
            "SELECT A.ChatRoomName,A.UserNameList, A.DisplayNameList,A.RoomData, B.Announcement,B.AnnouncementEditor "
            "FROM ChatRoom A,ChatRoomInfo B "
            "where A.ChatRoomName==B.ChatRoomName "
            "ORDER BY A.ChatRoomName ASC;")
        if roomwxid:
            sql = sql.replace("ORDER BY A.ChatRoomName ASC;",
                              f"and A.ChatRoomName LIKE '%{roomwxid}%' "
                              "ORDER BY A.ChatRoomName ASC;")
        result = self.execute_sql(sql)
        if not result:
            return []
        room_datas = []
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            ChatRoomName, UserNameList, DisplayNameList, RoomData, Announcement, AnnouncementEditor = row
            UserNameList = UserNameList.split("^G")
            DisplayNameList = DisplayNameList.split("^G")
            RoomData = self.ChatRoom_RoomData(RoomData)
            wxid2remark = {}
            if RoomData:
                rd = []
                for k, v in RoomData.items():
                    if isinstance(v, list):
                        rd += v
                for i in rd:
                    try:
                        if isinstance(i, dict) and isinstance(i.get('1'), str) and i.get('2'):
                            wxid2remark[i['1']] = i["2"]
                    except Exception as e:
                        logging.error(f"wxid2remark: ChatRoomName:{ChatRoomName}, {i} error:{e}")
            rooms.append(
                {"ChatRoomName": ChatRoomName, "UserNameList": UserNameList, "DisplayNameList": DisplayNameList,
                 "Announcement": Announcement, "AnnouncementEditor": AnnouncementEditor, "wxid2remark": wxid2remark})
        return rooms

    def labels_dict(self, id_is_key=True):
        """
        读取标签列表
        :param label_list:
        :return:
        """
        sql = "SELECT LabelId, LabelName FROM ContactLabel ORDER BY LabelName ASC;"
        result = self.execute_sql(sql)
        if not result:
            return []
        if id_is_key:
            labels = {row[0]: row[1] for row in result}
        else:
            labels = {row[1]: row[0] for row in result}
        return labels
