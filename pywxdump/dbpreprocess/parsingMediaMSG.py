# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         MediaMSG_parsing.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
from .dbbase import DatabaseBase
from .utils import silk2audio


class ParsingMediaMSG(DatabaseBase):
    _class_name = "MediaMSG"
    def __init__(self, db_path):
        super().__init__(db_path)

    def get_audio(self, MsgSvrID, is_play=False, is_wave=False, save_path=None, rate=24000):
        sql = "select Buf from Media where Reserved0=? "
        DBdata = self.execute_sql(sql, (MsgSvrID,))
        if not DBdata:
            return False
        if len(DBdata) == 0:
            return False
        data = DBdata[0][0]  # [1:] + b'\xFF\xFF'
        try:
            pcm_data = silk2audio(buf_data=data, is_play=is_play, is_wave=is_wave, save_path=save_path, rate=rate)
            return pcm_data
        except Exception as e:
            return False
