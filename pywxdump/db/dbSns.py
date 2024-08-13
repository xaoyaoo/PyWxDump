# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         Sns.py
# Description:  负责处理朋友圈相关数据
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
from .dbbase import DatabaseBase
from .utils import silk2audio


class SnsHandler(DatabaseBase):
    _class_name = "Sns"
    Media_required_tables = ["AdFeedsV8", "FeedsV20", "CommentV20", "NotificationV7", "SnsConfigV20", "SnsFailureV5",
                             "SnsGroupInfoV5", "SnsNoNotifyV5"]
    """
    FeedsV20：朋友圈的XML数据
    CommentV20：朋友圈点赞或评论记录
    NotificationV7：朋友圈通知
    SnsConfigV20：一些配置信息，能读懂的是其中有你的朋友圈背景图
    SnsGroupInfoV5：猜测是旧版微信朋友圈可见范围的可见或不可见名单
    """
