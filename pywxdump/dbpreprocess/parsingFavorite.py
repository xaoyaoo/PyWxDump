# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parsingFavorite.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/05/18
# -------------------------------------------------------------------------------
from .dbbase import DatabaseBase

# * FavItems：收藏的消息条目列表
# * FavDataItem：收藏的具体数据。大概可以确定以下两点
#     * 即使只是简单收藏一篇公众号文章也会在 FavDataItem 中有一个对应的记录
#     * 对于收藏的合并转发类型的消息，合并转发中的每一条消息在 FavDataItem 中都是一个独立的记录
# * FavTags：为收藏内容添加的标签

class ParsingFavorite(DatabaseBase):
    _class_name = "Favorite"

    def __init__(self, db_path):
        super().__init__(db_path)

    def get_favorite(self):
        sql1 = "select * from FavItems"
        sql2 = "select * from FavDataItem"
        sql3 = "select * from FavTags"
        DBdata1 = self.execute_sql(sql1)
        DBdata2 = self.execute_sql(sql2)
        DBdata3 = self.execute_sql(sql3)
        return DBdata1, DBdata2, DBdata3