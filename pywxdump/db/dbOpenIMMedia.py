# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         MediaMSG_parsing.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
from .dbbase import DatabaseBase
from .utils import silk2audio, db_loger


class OpenIMMediaHandler(DatabaseBase):
    _class_name = "OpenIMMedia"
    OpenIMMedia_required_tables = ["OpenIMMedia"]

    def OpenIMMedia_tables_exist(self):
        """
        判断该类所需要的表是否存在
        """
        return self.check_tables_exist(self.OpenIMMedia_required_tables)

    def get_im_audio(self, MsgSvrID, is_play=False, is_wave=False, save_path=None, rate=24000):
        sql = "select Buf from OpenIMMedia where Reserved0=? "
        DBdata = self.execute(sql, (MsgSvrID,))
        if not DBdata:
            return False
        if len(DBdata) == 0:
            return False
        data = DBdata[0][0]  # [1:] + b'\xFF\xFF'
        try:
            pcm_data = silk2audio(buf_data=data, is_play=is_play, is_wave=is_wave, save_path=save_path, rate=rate)
            return pcm_data
        except Exception as e:
            db_loger.warning(e, exc_info=True)
            return False
