# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         MicroMsg.py
# Description:  负责处理联系人数据库
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
import logging

from .dbbase import DatabaseBase
from .utils import timestamp2str, bytes2str, db_loger, db_error

import blackboxprotobuf


class MicroHandler(DatabaseBase):
    _class_name = "MicroMsg"
    Micro_required_tables = ["ContactLabel", "Contact", "ContactHeadImgUrl", "Session", "ChatInfo", "ChatRoom",
                             "ChatRoomInfo"]

    def Micro_add_index(self):
        """
        添加索引, 加快查询速度
        """
        # 为 Session 表添加索引
        if self.tables_exist("Session"):
            self.execute("CREATE INDEX IF NOT EXISTS idx_Session_strUsrName_nTime ON Session(strUsrName, nTime);")
            self.execute("CREATE INDEX IF NOT EXISTS idx_Session_nOrder ON Session(nOrder);")
            self.execute("CREATE INDEX IF NOT EXISTS idx_Session_nTime ON Session(nTime);")

        # 为 Contact 表添加索引

        if self.tables_exist("Contact"):
            self.execute("CREATE INDEX IF NOT EXISTS idx_Contact_UserName ON Contact(UserName);")

        # 为 ContactHeadImgUrl 表添加索引
        if self.tables_exist('ContactHeadImgUrl'):
            self.execute("CREATE INDEX IF NOT EXISTS idx_ContactHeadImgUrl_usrName ON ContactHeadImgUrl(usrName);")

        # 为 ChatInfo 表添加索引
        if self.tables_exist('ChatInfo'):
            self.execute("CREATE INDEX IF NOT EXISTS idx_ChatInfo_Username_LastReadedCreateTime "
                         "ON ChatInfo(Username, LastReadedCreateTime);")
            self.execute(
                "CREATE INDEX IF NOT EXISTS idx_ChatInfo_LastReadedCreateTime ON ChatInfo(LastReadedCreateTime);")

        # 为 Contact 表添加复合索引
        if self.tables_exist('Contact'):
            self.execute("CREATE INDEX IF NOT EXISTS idx_Contact_search "
                         "ON Contact(UserName, NickName, Remark, Alias, QuanPin, PYInitial, RemarkQuanPin, RemarkPYInitial);")

        # 为 ChatRoom 和 ChatRoomInfo 表添加索引
        if self.tables_exist(['ChatRoomInfo', "ChatRoom"]):
            self.execute("CREATE INDEX IF NOT EXISTS idx_ChatRoom_ChatRoomName ON ChatRoom(ChatRoomName);")
            self.execute("CREATE INDEX IF NOT EXISTS idx_ChatRoomInfo_ChatRoomName ON ChatRoomInfo(ChatRoomName);")

    @db_error
    def get_labels(self, id_is_key=True):
        """
        读取标签列表
        :param id_is_key: id_is_key: True: id作为key，False: name作为key
        :return:
        """
        labels = {}
        if not self.tables_exist("ContactLabel"):
            return labels
        sql = "SELECT LabelId, LabelName FROM ContactLabel ORDER BY LabelName ASC;"
        result = self.execute(sql)
        if not result:
            return labels
        if id_is_key:
            labels = {row[0]: row[1] for row in result}
        else:
            labels = {row[1]: row[0] for row in result}
        return labels

    @db_error
    def get_session_list(self):
        """
        获取会话列表
        :return: 会话列表
        """
        sessions = {}
        if not self.tables_exist(["Session", "Contact", "ContactHeadImgUrl"]):
            return sessions
        sql = (
            "SELECT S.strUsrName,S.nOrder,S.nUnReadCount, S.strNickName, S.nStatus, S.nIsSend, S.strContent, "
            "S.nMsgLocalID, S.nMsgStatus, S.nTime, S.nMsgType, S.Reserved2 AS nMsgSubType, C.UserName, C.Alias, "
            "C.DelFlag, C.Type, C.VerifyFlag, C.Reserved1, C.Reserved2, C.Remark, C.NickName, C.LabelIDList, "
            "C.ChatRoomType, C.ChatRoomNotify, C.Reserved5, C.Reserved6 as describe, C.ExtraBuf, H.bigHeadImgUrl "
            "FROM (SELECT strUsrName, MAX(nTime) AS MaxnTime FROM Session GROUP BY strUsrName) AS SubQuery "
            "JOIN Session S ON S.strUsrName = SubQuery.strUsrName AND S.nTime = SubQuery.MaxnTime "
            "left join Contact C ON C.UserName = S.strUsrName "
            "LEFT JOIN ContactHeadImgUrl H ON C.UserName = H.usrName "
            "WHERE S.strUsrName!='@publicUser' "
            "ORDER BY S.nTime DESC;"
        )

        db_loger.info(f"get_session_list sql: {sql}")
        ret = self.execute(sql)
        if not ret:
            return sessions

        id2label = self.get_labels()
        for row in ret:
            (strUsrName, nOrder, nUnReadCount, strNickName, nStatus, nIsSend, strContent,
             nMsgLocalID, nMsgStatus, nTime, nMsgType, nMsgSubType,
             UserName, Alias, DelFlag, Type, VerifyFlag, Reserved1, Reserved2, Remark, NickName, LabelIDList,
             ChatRoomType, ChatRoomNotify, Reserved5, describe, ExtraBuf, bigHeadImgUrl) = row

            ExtraBuf = get_ExtraBuf(ExtraBuf)
            LabelIDList = LabelIDList.split(",") if LabelIDList else []
            LabelIDList = [id2label.get(int(label_id), label_id) for label_id in LabelIDList if label_id]
            nTime = timestamp2str(nTime) if nTime else None

            sessions[strUsrName] = {
                "wxid": strUsrName, "nOrder": nOrder, "nUnReadCount": nUnReadCount, "strNickName": strNickName,
                "nStatus": nStatus, "nIsSend": nIsSend, "strContent": strContent, "nMsgLocalID": nMsgLocalID,
                "nMsgStatus": nMsgStatus, "nTime": nTime, "nMsgType": nMsgType, "nMsgSubType": nMsgSubType,
                "LastReadedCreateTime": nTime,
                "nickname": NickName, "remark": Remark, "account": Alias,
                "describe": describe, "headImgUrl": bigHeadImgUrl if bigHeadImgUrl else "",
                "ExtraBuf": ExtraBuf, "LabelIDList": tuple(LabelIDList)
            }
        return sessions

    @db_error
    def get_recent_chat_wxid(self):
        """
        获取最近聊天的联系人
        :return: 最近聊天的联系人
        """
        users = []
        if not self.tables_exist(["ChatInfo"]):
            return users
        sql = (
            "SELECT A.Username, LastReadedCreateTime, LastReadedSvrId "
            "FROM (   SELECT Username, MAX(LastReadedCreateTime) AS MaxLastReadedCreateTime  FROM ChatInfo "
            "WHERE LastReadedCreateTime IS NOT NULL AND LastReadedCreateTime > 1007911408000   GROUP BY Username "
            ") AS SubQuery JOIN ChatInfo A "
            "ON A.Username = SubQuery.Username AND LastReadedCreateTime = SubQuery.MaxLastReadedCreateTime "
            "ORDER BY A.LastReadedCreateTime DESC;"
        )

        db_loger.info(f"get_recent_chat_wxid sql: {sql}")
        result = self.execute(sql)
        if not result:
            return []
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            username, LastReadedCreateTime, LastReadedSvrId = row
            LastReadedCreateTime = timestamp2str(LastReadedCreateTime) if LastReadedCreateTime else None
            users.append(
                {"wxid": username, "LastReadedCreateTime": LastReadedCreateTime, "LastReadedSvrId": LastReadedSvrId})
        return users

    @db_error
    def get_user_list(self, word: str = None, wxids: list = None, label_ids: list = None):
        """
        获取联系人列表
        [ 注意：如果修改这个函数，要同时修改dbOpenIMContact.py中的get_im_user_list函数 ]
        :param word: 查询关键字，可以是wxid,用户名、昵称、备注、描述，允许拼音
        :param wxids: wxid列表
        :param label_ids: 标签id
        :return: 联系人字典
        """
        if isinstance(wxids, str):
            wxids = [wxids]
        if isinstance(label_ids, str):
            label_ids = [label_ids]

        users = {}
        if not self.tables_exist(["Contact", "ContactHeadImgUrl"]):
            return users
        sql = (
            "SELECT A.UserName, A.Alias, A.DelFlag, A.Type, A.VerifyFlag, A.Reserved1, A.Reserved2,"
            "A.Remark, A.NickName, A.LabelIDList, A.ChatRoomType, A.ChatRoomNotify, A.Reserved5,"
            "A.Reserved6 as describe, A.ExtraBuf, B.bigHeadImgUrl "
            "FROM Contact A LEFT JOIN ContactHeadImgUrl B ON A.UserName = B.usrName WHERE 1==1 ;"
        )
        if word:
            sql = sql.replace(";",
                              f"AND ( A.UserName LIKE '%{word}%' "
                              f"OR A.NickName LIKE '%{word}%' "
                              f"OR A.Remark LIKE '%{word}%' "
                              f"OR A.Alias LIKE '%{word}%' "
                              f"OR LOWER(A.QuanPin) LIKE LOWER('%{word}%') "
                              f"OR LOWER(A.PYInitial) LIKE LOWER('%{word}%') "
                              f"OR LOWER(A.RemarkQuanPin) LIKE LOWER('%{word}%') "
                              f"OR LOWER(A.RemarkPYInitial) LIKE LOWER('%{word}%') "
                              f") "
                              ";")
        if wxids:
            sql = sql.replace(";", f"AND A.UserName IN ('" + "','".join(wxids) + "') ;")

        if label_ids:
            sql_label = [f"A.LabelIDList LIKE '%{i}%' " for i in label_ids]
            sql_label = " OR ".join(sql_label)
            sql = sql.replace(";", f"AND ({sql_label}) ;")

        db_loger.info(f"get_user_list sql: {sql}")
        result = self.execute(sql)
        if not result:
            return users
        id2label = self.get_labels()
        for row in result:
            # 获取wxid,昵称，备注，描述，头像,标签
            (UserName, Alias, DelFlag, Type, VerifyFlag, Reserved1, Reserved2, Remark, NickName, LabelIDList,
             ChatRoomType, ChatRoomNotify, Reserved5, describe, ExtraBuf, bigHeadImgUrl) = row

            ExtraBuf = get_ExtraBuf(ExtraBuf)
            LabelIDList = LabelIDList.split(",") if LabelIDList else []
            LabelIDList = [id2label.get(int(label_id), label_id) for label_id in LabelIDList if label_id]

            # print(f"{UserName=}\n{Alias=}\n{DelFlag=}\n{Type=}\n{VerifyFlag=}\n{Reserved1=}\n{Reserved2=}\n"
            #       f"{Remark=}\n{NickName=}\n{LabelIDList=}\n{ChatRoomType=}\n{ChatRoomNotify=}\n{Reserved5=}\n"
            #       f"{describe=}\n{ExtraBuf=}\n{bigHeadImgUrl=}")
            users[UserName] = {
                "wxid": UserName, "nickname": NickName, "remark": Remark, "account": Alias,
                "describe": describe, "headImgUrl": bigHeadImgUrl if bigHeadImgUrl else "",
                "ExtraBuf": ExtraBuf, "LabelIDList": tuple(LabelIDList),
                "extra": None}
        extras = self.get_room_list(roomwxids=filter(lambda x: "@" in x, users.keys()))
        for UserName in users:
            users[UserName]["extra"] = extras.get(UserName, None)
        return users

    @db_error
    def get_room_list(self, word=None, roomwxids: list = None):
        """
        获取群聊列表
        :param word: 群聊搜索词
        :param roomwxids: 群聊wxid列表
        :return: 群聊字典
        """
        # 连接 MicroMsg.db 数据库，并执行查询
        if isinstance(roomwxids, str):
            roomwxids = [roomwxids]

        rooms = {}
        if not self.tables_exist(["ChatRoom", "ChatRoomInfo"]):
            return rooms
        sql = (
            "SELECT A.ChatRoomName,A.UserNameList,A.DisplayNameList,A.ChatRoomFlag,A.IsShowName,"
            "A.SelfDisplayName,A.Reserved2,A.RoomData, "
            "B.Announcement,B.AnnouncementEditor,B.AnnouncementPublishTime "
            "FROM ChatRoom A LEFT JOIN ChatRoomInfo B ON A.ChatRoomName==B.ChatRoomName "
            "WHERE 1==1 ;")
        if word:
            sql = sql.replace(";",
                              f"AND A.ChatRoomName LIKE '%{word}%' ;")
        if roomwxids:
            sql = sql.replace(";", f"AND A.ChatRoomName IN ('" + "','".join(roomwxids) + "') ;")

        db_loger.info(f"get_room_list sql: {sql}")
        result = self.execute(sql)
        if not result:
            return rooms

        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            (ChatRoomName, UserNameList, DisplayNameList, ChatRoomFlag, IsShowName, SelfDisplayName,
             Reserved2, RoomData,
             Announcement, AnnouncementEditor, AnnouncementPublishTime) = row

            UserNameList = UserNameList.split("^G")
            DisplayNameList = DisplayNameList.split("^G")

            RoomData = ChatRoom_RoomData(RoomData)
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
                        db_loger.error(f"wxid2remark: ChatRoomName:{ChatRoomName}, {i} error:{e}", exc_info=True)
            rooms[ChatRoomName] = {
                "wxid": ChatRoomName, "UserNameList": UserNameList, "DisplayNameList": DisplayNameList,
                "ChatRoomFlag": ChatRoomFlag, "IsShowName": IsShowName, "SelfDisplayName": SelfDisplayName,
                "owner": Reserved2, "wxid2remark": wxid2remark,
                "Announcement": Announcement, "AnnouncementEditor": AnnouncementEditor,
                "AnnouncementPublishTime": AnnouncementPublishTime}
        return rooms


@db_error
def ChatRoom_RoomData(RoomData):
    # 读取群聊数据,主要为 wxid，以及对应昵称
    if RoomData is None or not isinstance(RoomData, bytes):
        return None
    data = get_BytesExtra(RoomData)
    bytes2str(data) if data else None
    return data


@db_error
def get_BytesExtra(BytesExtra):
    if BytesExtra is None or not isinstance(BytesExtra, bytes):
        return None
    try:
        deserialize_data, message_type = blackboxprotobuf.decode_message(BytesExtra)
        return deserialize_data
    except Exception as e:
        db_loger.warning(f"\nget_BytesExtra: {e}\n{BytesExtra}", exc_info=True)
        return None


@db_error
def get_ExtraBuf(ExtraBuf: bytes):
    """
    读取ExtraBuf（联系人表）
    :param ExtraBuf:
    :return:
    """
    if not ExtraBuf:
        return None
    buf_dict = {
        '74752C06': '性别[1男2女]', '46CF10C4': '个性签名', 'A4D9024A': '国', 'E2EAA8D1': '省', '1D025BBF': '市',
        'F917BCC0': '公司名称', '759378AD': '手机号', '4EB96D85': '企微属性', '81AE19B4': '朋友圈背景',
        '0E719F13': '备注图片', '945f3190': '备注图片2',
        'DDF32683': '0', '88E28FCE': '1', '761A1D2D': '2', '0263A0CB': '3', '0451FF12': '4', '228C66A8': '5',
        '4D6C4570': '6', '4335DFDD': '7', 'DE4CDAEB': '8', 'A72BC20A': '9', '069FED52': '10', '9B0F4299': '11',
        '3D641E22': '12', '1249822C': '13', 'B4F73ACB': '14', '0959EB92': '15', '3CF4A315': '16',
        'C9477AC60201E44CD0E8': '17', 'B7ACF0F5': '18', '57A7B5A8': '19', '695F3170': '20', 'FB083DD9': '21',
        '0240E37F': '22', '315D02A3': '23', '7DEC0BC3': '24', '16791C90': '25'
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
            rdata[rdata_name] = ExtraBuf[offset + 4: offset + 4 + length].decode("utf-8", errors="ignore").rstrip(
                "\x00")
        elif type_id == b"\x05":
            rdata[rdata_name] = f"0x{ExtraBuf[offset: offset + 8].hex()}"
    return rdata
