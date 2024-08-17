# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         MSG.py
# Description:  负责处理消息数据库数据
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
import json
import os
import re
# import time

# import pandas as pd

from .dbbase import DatabaseBase
from .utils import db_error, timestamp2str, xml2dict, match_BytesExtra, type_converter, \
    get_md5, name2typeid, db_loger
import lz4.block
import blackboxprotobuf


class MsgHandler(DatabaseBase):
    _class_name = "MSG"
    MSG_required_tables = ["MSG"]

    def Msg_add_index(self):
        """
        添加索引,加快查询速度
        """
        # 检查是否存在索引
        if not self.tables_exist("MSG"):
            return
        self.execute("CREATE INDEX IF NOT EXISTS idx_MSG_StrTalker ON MSG(StrTalker);")
        self.execute("CREATE INDEX IF NOT EXISTS idx_MSG_CreateTime ON MSG(CreateTime);")
        self.execute("CREATE INDEX IF NOT EXISTS idx_MSG_StrTalker_CreateTime ON MSG(StrTalker, CreateTime);")

    @db_error
    def get_m_msg_count(self, wxids: list = ""):
        """
        获取聊天记录数量,根据wxid获取单个联系人的聊天记录数量，不传wxid则获取所有联系人的聊天记录数量
        :param wxids: wxid list
        :return: 聊天记录数量列表 {wxid: chat_count, total: total_count}
        """
        if isinstance(wxids, str) and wxids:
            wxids = [wxids]
        if wxids:
            wxids = "('" + "','".join(wxids) + "')"
            sql = f"SELECT StrTalker, COUNT(*) FROM MSG WHERE StrTalker IN {wxids} GROUP BY StrTalker ORDER BY COUNT(*) DESC;"
        else:
            sql = f"SELECT StrTalker, COUNT(*) FROM MSG GROUP BY StrTalker ORDER BY COUNT(*) DESC;"
        sql_total = f"SELECT COUNT(*) FROM MSG;"

        if not self.tables_exist("MSG"):
            return {}
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
    def get_msg_list(self, wxid="", start_index=0, page_size=500, msg_type: str = "", msg_sub_type: str = "",
                     start_createtime=None, end_createtime=None, my_talker="我"):
        """
        获取聊天记录列表
        :param wxid: wxid
        :param start_index: 起始索引
        :param page_size: 页大小
        :param msg_type: 消息类型
        :param msg_sub_type: 消息子类型
        :param start_createtime: 开始时间
        :param end_createtime: 结束时间
        :param my_talker: 我
        :return: 聊天记录列表 {"id": _id, "MsgSvrID": str(MsgSvrID), "type_name": type_name, "is_sender": IsSender,
                    "talker": talker, "room_name": StrTalker, "msg": msg, "src": src, "extra": {},
                    "CreateTime": CreateTime, }
        """
        if not self.tables_exist("MSG"):
            return [], []

        param = ()
        sql_wxid, param = ("AND StrTalker=? ", param + (wxid,)) if wxid else ("", param)
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
            "FROM MSG WHERE 1=1 "
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

    @db_error
    def get_date_count(self, wxid='', start_time: int = 0, end_time: int = 0, time_format='%Y-%m-%d'):
        """
        获取每日聊天记录数量，包括发送者数量、接收者数量和总数。
        """
        if not self.tables_exist("MSG"):
            return {}
        if isinstance(start_time, str) and start_time.isdigit():
            start_time = int(start_time)
        if isinstance(end_time, str) and end_time.isdigit():
            end_time = int(end_time)

        # if start_time or end_time is not an integer and not a float, set both to 0
        if not (isinstance(start_time, (int, float)) and isinstance(end_time, (int, float))):
            start_time = 0
            end_time = 0
        params = ()

        sql_wxid = "AND StrTalker = ? " if wxid else ""
        params = params + (wxid,) if wxid else params

        sql_time = "AND CreateTime BETWEEN ? AND ? " if start_time and end_time else ""
        params = params + (start_time, end_time) if start_time and end_time else params

        sql = (f"SELECT strftime('{time_format}', CreateTime, 'unixepoch', 'localtime') AS date, "
               "       COUNT(*) AS total_count ,"
               "       SUM(CASE WHEN IsSender = 1 THEN 1 ELSE 0 END) AS sender_count, "
               "       SUM(CASE WHEN IsSender = 0 THEN 1 ELSE 0 END) AS receiver_count "
               "FROM MSG "
               "WHERE StrTalker NOT LIKE '%chatroom%' "
               f"{sql_wxid} {sql_time} "
               f"GROUP BY date ORDER BY date ASC;")
        result = self.execute(sql, params)

        if not result:
            return {}
        # 将查询结果转换为字典
        result_dict = {}
        for row in result:
            date, total_count, sender_count, receiver_count = row
            result_dict[date] = {
                "sender_count": sender_count,
                "receiver_count": receiver_count,
                "total_count": total_count
            }
        return result_dict

    @db_error
    def get_top_talker_count(self, top: int = 10, start_time: int = 0, end_time: int = 0):
        """
        获取聊天记录数量最多的联系人,他们聊天记录数量
        """
        if not self.tables_exist("MSG"):
            return {}
        if isinstance(start_time, str) and start_time.isdigit():
            start_time = int(start_time)
        if isinstance(end_time, str) and end_time.isdigit():
            end_time = int(end_time)

        # if start_time or end_time is not an integer and not a float, set both to 0
        if not (isinstance(start_time, (int, float)) and isinstance(end_time, (int, float))):
            start_time = 0
            end_time = 0

        sql_time = f"AND CreateTime BETWEEN {start_time} AND {end_time} " if start_time and end_time else ""
        sql = (
            "SELECT StrTalker, COUNT(*) AS count,"
            "SUM(CASE WHEN IsSender = 1 THEN 1 ELSE 0 END) AS sender_count, "
            "SUM(CASE WHEN IsSender = 0 THEN 1 ELSE 0 END) AS receiver_count "
            "FROM MSG "
            "WHERE StrTalker NOT LIKE '%chatroom%' "
            f"{sql_time} "
            "GROUP BY StrTalker ORDER BY count DESC "
            f"LIMIT {top};"
        )
        result = self.execute(sql)
        if not result:
            return {}
        # 将查询结果转换为字典
        result_dict = {row[0]: {"total_count": row[1], "sender_count": row[2], "receiver_count": row[3]} for row in
                       result}
        return result_dict

    # 单条消息处理
    @db_error
    def get_msg_detail(self, row, my_talker="我"):
        """
        获取单条消息详情,格式化输出
        """
        (localId, TalkerId, MsgSvrID, Type, SubType, CreateTime, IsSender, Sequence, StatusEx, FlagEx, Status,
         MsgSequence, StrContent, MsgServerSeq, StrTalker, DisplayContent, Reserved0, Reserved1, Reserved3,
         Reserved4, Reserved5, Reserved6, CompressContent, BytesExtra, BytesTrans, Reserved2, _id) = row

        CreateTime = timestamp2str(CreateTime)

        type_id = (Type, SubType)
        type_name = type_converter(type_id)

        msg = StrContent
        src = ""
        extra = {}

        if type_id == (1, 0):  # 文本
            msg = StrContent

        elif type_id == (3, 0):  # 图片
            DictExtra = get_BytesExtra(BytesExtra)
            DictExtra_str = str(DictExtra)
            img_paths = [i for i in re.findall(r"(FileStorage.*?)'", DictExtra_str)]
            img_paths = sorted(img_paths, key=lambda p: "Image" in p, reverse=True)
            if img_paths:
                img_path = img_paths[0].replace("'", "")
                img_path = [i for i in img_path.split("\\") if i]
                img_path = os.path.join(*img_path)
                src = img_path
            else:
                src = ""
            msg = "图片"
        elif type_id == (34, 0):  # 语音
            tmp_c = xml2dict(StrContent)
            voicelength = tmp_c.get("voicemsg", {}).get("voicelength", "")
            transtext = tmp_c.get("voicetrans", {}).get("transtext", "")
            if voicelength.isdigit():
                voicelength = int(voicelength) / 1000
                voicelength = f"{voicelength:.2f}"
            msg = f"语音时长：{voicelength}秒\n翻译结果：{transtext}" if transtext else f"语音时长：{voicelength}秒"
            src = os.path.join(f"{StrTalker}",
                               f"{CreateTime.replace(':', '-').replace(' ', '_')}_{IsSender}_{MsgSvrID}.wav")
        elif type_id == (43, 0):  # 视频
            DictExtra = get_BytesExtra(BytesExtra)
            DictExtra = str(DictExtra)

            DictExtra_str = str(DictExtra)
            video_paths = [i for i in re.findall(r"(FileStorage.*?)'", DictExtra_str)]
            video_paths = sorted(video_paths, key=lambda p: "mp4" in p, reverse=True)
            if video_paths:
                video_path = video_paths[0].replace("'", "")
                video_path = [i for i in video_path.split("\\") if i]
                video_path = os.path.join(*video_path)
                src = video_path
            else:
                src = ""
            msg = "视频"

        elif type_id == (47, 0):  # 动画表情
            content_tmp = xml2dict(StrContent)
            cdnurl = content_tmp.get("emoji", {}).get("cdnurl", "")
            if not cdnurl:
                DictExtra = get_BytesExtra(BytesExtra)
                cdnurl = match_BytesExtra(DictExtra)
            if cdnurl:
                msg, src = "表情", cdnurl

        elif type_id == (48, 0):  # 地图信息
            content_tmp = xml2dict(StrContent)
            location = content_tmp.get("location", {})
            msg = (f"纬度:【{location.pop('x')}】 经度:【{location.pop('y')}】\n"
                   f"位置：{location.pop('label')} {location.pop('poiname')}\n"
                   f"其他信息：{json.dumps(location, ensure_ascii=False, indent=4)}"
                   )
            src = ""
        elif type_id == (49, 0):  # 文件
            DictExtra = get_BytesExtra(BytesExtra)
            url = match_BytesExtra(DictExtra)
            src = url
            file_name = os.path.basename(url)
            msg = file_name

        elif type_id == (49, 5):  # (分享)卡片式链接
            CompressContent = decompress_CompressContent(CompressContent)
            CompressContent_tmp = xml2dict(CompressContent)
            appmsg = CompressContent_tmp.get("appmsg", {})
            title = appmsg.get("title", "")
            des = appmsg.get("des", "")
            url = appmsg.get("url", "")
            msg = f'{title}\n{des}\n\n<a href="{url}" target="_blank">点击查看详情</a>'
            src = url
            extra = appmsg

        elif type_id == (49, 19):  # 合并转发的聊天记录
            CompressContent = decompress_CompressContent(CompressContent)
            content_tmp = xml2dict(CompressContent)
            title = content_tmp.get("appmsg", {}).get("title", "")
            des = content_tmp.get("appmsg", {}).get("des", "")
            recorditem = content_tmp.get("appmsg", {}).get("recorditem", "")
            recorditem = xml2dict(recorditem)
            msg = f"{title}\n{des}"
            src = recorditem

        elif type_id == (49, 57):  # 带有引用的文本消息
            CompressContent = decompress_CompressContent(CompressContent)
            content_tmp = xml2dict(CompressContent)
            appmsg = content_tmp.get("appmsg", {})

            title = appmsg.get("title", "")
            refermsg = appmsg.get("refermsg", {})

            type_id = appmsg.get("type", "1")

            displayname = refermsg.get("displayname", "")
            display_content = refermsg.get("content", "")
            display_createtime = refermsg.get("createtime", "")

            display_createtime = timestamp2str(
                int(display_createtime)) if display_createtime.isdigit() else display_createtime

            if display_content and display_content.startswith("<?xml"):
                display_content = xml2dict(display_content)
                if "img" in display_content:
                    display_content = "图片"
                else:
                    appmsg1 = display_content.get("appmsg", {})
                    title1 = appmsg1.get("title", "")
                    display_content = title1 if title1 else display_content
            msg = f"{title}\n\n[引用]({display_createtime}){displayname}:{display_content}"
            src = ""

        elif type_id == (49, 2000):  # 转账消息
            CompressContent = decompress_CompressContent(CompressContent)
            content_tmp = xml2dict(CompressContent)
            wcpayinfo = content_tmp.get("appmsg", {}).get("wcpayinfo", {})
            paysubtype = wcpayinfo.get("paysubtype", "")  # 转账类型
            feedesc = wcpayinfo.get("feedesc", "")  # 转账金额
            pay_memo = wcpayinfo.get("pay_memo", "")  # 转账备注
            begintransfertime = wcpayinfo.get("begintransfertime", "")  # 转账开始时间
            msg = (f"{'已收款' if paysubtype == '3' else '转账'}：{feedesc}\n"
                   f"转账说明：{pay_memo if pay_memo else ''}\n"
                   f"转账时间：{timestamp2str(begintransfertime)}\n"
                   )
            src = ""

        elif type_id[0] == 49 and type_id[1] != 0:
            DictExtra = get_BytesExtra(BytesExtra)
            url = match_BytesExtra(DictExtra)
            src = url
            msg = type_name

        elif type_id == (50, 0):  # 语音通话
            msg = "语音/视频通话[%s]" % DisplayContent

        # elif type_id == (10000, 0):
        #     msg = StrContent
        # elif type_id == (10000, 4):
        #     msg = StrContent
        # elif type_id == (10000, 8000):
        #     msg = StrContent

        talker = "未知"
        if IsSender == 1:
            talker = my_talker
        else:
            if StrTalker.endswith("@chatroom"):
                bytes_extra = get_BytesExtra(BytesExtra)
                if bytes_extra:
                    try:
                        talker = bytes_extra['3'][0]['2']
                        if "publisher-id" in talker:
                            talker = "系统"
                    except:
                        pass
            else:
                talker = StrTalker

        row_data = {"id": _id, "MsgSvrID": str(MsgSvrID), "type_name": type_name, "is_sender": IsSender,
                    "talker": talker, "room_name": StrTalker, "msg": msg, "src": src, "extra": extra,
                    "CreateTime": CreateTime, }
        return row_data


@db_error
def decompress_CompressContent(data):
    """
    解压缩Msg：CompressContent内容
    :param data: CompressContent内容 bytes
    :return:
    """
    if data is None or not isinstance(data, bytes):
        return None
    try:
        dst = lz4.block.decompress(data, uncompressed_size=len(data) << 8)
        dst = dst.replace(b'\x00', b'')  # 已经解码完成后，还含有0x00的部分，要删掉，要不后面ET识别的时候会报错
        uncompressed_data = dst.decode('utf-8', errors='ignore')
        return uncompressed_data
    except Exception as e:
        return data.decode('utf-8', errors='ignore')


@db_error
def get_BytesExtra(BytesExtra):
    BytesExtra_message_type = {
        "1": {
            "type": "message",
            "message_typedef": {
                "1": {
                    "type": "int",
                    "name": ""
                },
                "2": {
                    "type": "int",
                    "name": ""
                }
            },
            "name": "1"
        },
        "3": {
            "type": "message",
            "message_typedef": {
                "1": {
                    "type": "int",
                    "name": ""
                },
                "2": {
                    "type": "str",
                    "name": ""
                }
            },
            "name": "3",
            "alt_typedefs": {
                "1": {
                    "1": {
                        "type": "int",
                        "name": ""
                    },
                    "2": {
                        "type": "message",
                        "message_typedef": {},
                        "name": ""
                    }
                },
                "2": {
                    "1": {
                        "type": "int",
                        "name": ""
                    },
                    "2": {
                        "type": "message",
                        "message_typedef": {
                            "13": {
                                "type": "fixed32",
                                "name": ""
                            },
                            "12": {
                                "type": "fixed32",
                                "name": ""
                            }
                        },
                        "name": ""
                    }
                },
                "3": {
                    "1": {
                        "type": "int",
                        "name": ""
                    },
                    "2": {
                        "type": "message",
                        "message_typedef": {
                            "15": {
                                "type": "fixed64",
                                "name": ""
                            }
                        },
                        "name": ""
                    }
                },
                "4": {
                    "1": {
                        "type": "int",
                        "name": ""
                    },
                    "2": {
                        "type": "message",
                        "message_typedef": {
                            "15": {
                                "type": "int",
                                "name": ""
                            },
                            "14": {
                                "type": "fixed32",
                                "name": ""
                            }
                        },
                        "name": ""
                    }
                },
                "5": {
                    "1": {
                        "type": "int",
                        "name": ""
                    },
                    "2": {
                        "type": "message",
                        "message_typedef": {
                            "12": {
                                "type": "fixed32",
                                "name": ""
                            },
                            "7": {
                                "type": "fixed64",
                                "name": ""
                            },
                            "6": {
                                "type": "fixed64",
                                "name": ""
                            }
                        },
                        "name": ""
                    }
                },
                "6": {
                    "1": {
                        "type": "int",
                        "name": ""
                    },
                    "2": {
                        "type": "message",
                        "message_typedef": {
                            "7": {
                                "type": "fixed64",
                                "name": ""
                            },
                            "6": {
                                "type": "fixed32",
                                "name": ""
                            }
                        },
                        "name": ""
                    }
                },
                "7": {
                    "1": {
                        "type": "int",
                        "name": ""
                    },
                    "2": {
                        "type": "message",
                        "message_typedef": {
                            "12": {
                                "type": "fixed64",
                                "name": ""
                            }
                        },
                        "name": ""
                    }
                },
                "8": {
                    "1": {
                        "type": "int",
                        "name": ""
                    },
                    "2": {
                        "type": "message",
                        "message_typedef": {
                            "6": {
                                "type": "fixed64",
                                "name": ""
                            },
                            "12": {
                                "type": "fixed32",
                                "name": ""
                            }
                        },
                        "name": ""
                    }
                },
                "9": {
                    "1": {
                        "type": "int",
                        "name": ""
                    },
                    "2": {
                        "type": "message",
                        "message_typedef": {
                            "15": {
                                "type": "int",
                                "name": ""
                            },
                            "12": {
                                "type": "fixed64",
                                "name": ""
                            },
                            "6": {
                                "type": "int",
                                "name": ""
                            }
                        },
                        "name": ""
                    }
                },
                "10": {
                    "1": {
                        "type": "int",
                        "name": ""
                    },
                    "2": {
                        "type": "message",
                        "message_typedef": {
                            "6": {
                                "type": "fixed32",
                                "name": ""
                            },
                            "12": {
                                "type": "fixed64",
                                "name": ""
                            }
                        },
                        "name": ""
                    }
                },
            }
        }
    }
    if BytesExtra is None or not isinstance(BytesExtra, bytes):
        return None
    try:
        deserialize_data, message_type = blackboxprotobuf.decode_message(BytesExtra, BytesExtra_message_type)
        return deserialize_data
    except Exception as e:
        return None
