# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         Sns.py
# Description:  负责处理朋友圈相关数据 软件只能看到在电脑微信浏览过的朋友圈记录
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
import json

from .dbbase import DatabaseBase
from .utils import silk2audio, xml2dict, timestamp2str


# FeedsV20：朋友圈的XML数据
# CommentV20：朋友圈点赞或评论记录
# NotificationV7：朋友圈通知
# SnsConfigV20：一些配置信息，能读懂的是其中有你的朋友圈背景图
# SnsGroupInfoV5：猜测是旧版微信朋友圈可见范围的可见或不可见名单

class SnsHandler(DatabaseBase):
    _class_name = "Sns"
    Media_required_tables = ["AdFeedsV8", "FeedsV20", "CommentV20", "NotificationV7", "SnsConfigV20", "SnsFailureV5",
                             "SnsGroupInfoV5", "SnsNoNotifyV5"]

    def get_sns_feed(self):
        """
        获取朋友圈数据
        http://shmmsns.qpic.cn/mmsns/uGxMq1C4wvppcjBbyweK796GtT1hH3LGISYajZ2v7C11XhHk5icyDUXcWNSPk2MooeIa8Es5hXP0/0?idx=1&token=WSEN6qDsKwV8A02w3onOGQYfxnkibdqSOkmHhZGNB4DFumlE9p1vp0e0xjHoXlbbXRzwnQia6X5t3Annc4oqTuDg
        """
        sql = (
            "SELECT FeedId, CreateTime, FaultId, Type, UserName, Status, ExtFlag, PrivFlag, StringId, Content "
            "FROM FeedsV20 "
            "ORDER BY CreateTime DESC")
        FeedsV20 = self.execute(sql)
        for row in FeedsV20[2:]:
            (FeedId, CreateTime, FaultId, Type, UserName, Status, ExtFlag, PrivFlag, StringId, Content) = row

            Content = xml2dict(Content) if Content and Content.startswith("<") else Content
            CreateTime = timestamp2str(CreateTime)
            print(
                f"{FeedId=}\n"
                f"{CreateTime=}\n"
                f"{FaultId=}\n"
                f"{Type=}\n"
                f"{UserName=}\n"
                f"{Status=}\n"
                f"{ExtFlag=}\n"
                f"{PrivFlag=}\n"
                f"{StringId=}\n\n"
                f"{json.dumps(Content, indent=4, ensure_ascii=False)}\n\n"
            )
            return FeedId, CreateTime, FaultId, Type, UserName, Status, ExtFlag, PrivFlag, StringId, Content

    def get_sns_comment(self):
        pass
