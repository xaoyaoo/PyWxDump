# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parsingFavorite.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/05/18
# -------------------------------------------------------------------------------
from .dbbase import DatabaseBase


class ParsingFavorite(DatabaseBase):
    _class_name = "Favorite"

    def __init__(self, db_path):
        super().__init__(db_path)

    def get_favorite(self):
        sql = "select * from FavItems"
        DBdata = self.execute_sql(sql)
        return DBdata
