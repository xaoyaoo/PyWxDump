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
        """
        sql = ("SELECT FeedId, CreateTime, FaultId, Type, UserName, Status, ExtFlag, PrivFlag, StringId, Content, "
               "Reserved1, Reserved2, Reserved3, Reserved4, Reserved5, Reserved6, ExtraBuf, Reserved7 "
               "FROM FeedsV20 "
               "ORDER BY CreateTime DESC")
        FeedsV20 = self.execute(sql)
        for row in FeedsV20[2:]:
            (FeedId, CreateTime, FaultId, Type, UserName, Status, ExtFlag, PrivFlag, StringId, Content,
             Reserved1, Reserved2, Reserved3, Reserved4, Reserved5, Reserved6, ExtraBuf, Reserved7) = row

            Content = xml2dict(Content) if Content and Content.startswith("<") else Content
            CreateTime = timestamp2str(CreateTime)
            print(f""
                  f"{FeedId=}\n"
                  f"{CreateTime=}\n"
                  f"{FaultId=}\n"
                  f"{Type=}\n"
                  f"{UserName=}\n"
                  f"{Status=}\n"
                  f"{ExtFlag=}\n"
                  f"{PrivFlag=}\n"
                  f"{StringId=}\n\n"
                  f"{json.dumps(Content,indent=4,ensure_ascii=False)}\n\n"
                  f"{ExtraBuf=}\n"
                  f"{Reserved1=}\n"
                  f"{Reserved2=}\n"
                  f"{Reserved3=}\n"
                  f"{Reserved4=}\n"
                  f"{Reserved5=}\n"
                  f"{Reserved6=}\n"
                  f"{Reserved7=}\n"
                  )

            break
