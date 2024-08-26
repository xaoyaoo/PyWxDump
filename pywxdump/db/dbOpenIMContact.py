# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         OpenIMContact.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/16
# -------------------------------------------------------------------------------
from .dbbase import DatabaseBase
from .utils import db_error


class OpenIMContactHandler(DatabaseBase):
    _class_name = "OpenIMContact"
    OpenIMContact_required_tables = ["OpenIMContact"]

    def get_im_user_list(self, word=None, wxids=None):
        """
        获取联系人列表
        [ 注意：如果修改这个函数，要同时修改dbMicro.py中的get_user_list函数 ]
        :param word: 查询关键字，可以是用户名、昵称、备注、描述，允许拼音
        :param wxids: 微信id列表
        :return: 联系人字典
        """
        if not self.tables_exist("OpenIMContact"):
            return []
        if not wxids:
            wxids = {}
        if isinstance(wxids, str):
            wxids = [wxids]
        sql = ("SELECT UserName,NickName,Type,Remark,BigHeadImgUrl,CustomInfoDetail,CustomInfoDetailVisible,"
               "AntiSpamTicket,AppId,Sex,DescWordingId,ExtraBuf "
               "FROM OpenIMContact WHERE 1==1 ;")
        if word:
            sql = sql.replace(";",
                              f"AND (UserName LIKE '%{word}%' "
                              f"OR NickName LIKE '%{word}%' "
                              f"OR Remark LIKE '%{word}%' "
                              f"OR LOWER(NickNamePYInit) LIKE LOWER('%{word}%') "
                              f"OR LOWER(NickNameQuanPin) LIKE LOWER('%{word}%') "
                              f"OR LOWER(RemarkPYInit) LIKE LOWER('%{word}%') "
                              f"OR LOWER(RemarkQuanPin) LIKE LOWER('%{word}%') "
                              ") ;")
        if wxids:
            sql = sql.replace(";", f"AND UserName IN ('" + "','".join(wxids) + "') ;")

        result = self.execute(sql)
        if not result:
            return {}

        users = {}
        for row in result:
            # 获取用户名、昵称、备注和聊天记录数量
            (UserName, NickName, Type, Remark, BigHeadImgUrl, CustomInfoDetail, CustomInfoDetailVisible,
             AntiSpamTicket, AppId, Sex, DescWordingId, ExtraBuf) = row

            users[UserName] = {
                "wxid": UserName, "nickname": NickName, "remark": Remark, "account": UserName,
                "describe": '', "headImgUrl": BigHeadImgUrl if BigHeadImgUrl else "",
                "ExtraBuf": None, "LabelIDList": tuple(), "extra": None}
        return users


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
