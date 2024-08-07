# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         __init__.py.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/14
# -------------------------------------------------------------------------------
# from .analyzer.db_parsing import read_img_dat, read_emoji, decompress_CompressContent, read_audio_buf, read_audio, \
#     parse_xml_string, read_BytesExtra
# from .ui import app_show_chat, get_user_list, export
from .wx_core import BiasAddr, get_wx_info, get_wx_db, batch_decrypt, decrypt, get_core_db
from .wx_core import merge_db, decrypt_merge, merge_real_time_db, all_merge_real_time_db
from .analyzer import DBPool
from .db import MsgHandler, MicroHandler, \
    MediaHandler, OpenIMContactHandler, FavoriteHandler, PublicMsgHandler, DBHandler
from .server import start_falsk
import os, json

try:
    WX_OFFS_PATH = os.path.join(os.path.dirname(__file__), "WX_OFFS.json")
    with open(WX_OFFS_PATH, "r", encoding="utf-8") as f:
        WX_OFFS = json.load(f)
except:
    WX_OFFS = {}
    WX_OFFS_PATH = None

# PYWXDUMP_ROOT_PATH = os.path.dirname(__file__)
# db_init = DBPool("DBPOOL_INIT")

__version__ = "3.1.13"
