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
from .wx_info import BiasAddr, read_info, get_wechat_db, batch_decrypt, decrypt, get_core_db
from .wx_info import merge_copy_db, merge_msg_db, merge_media_msg_db, merge_db, decrypt_merge, merge_real_time_db, \
    all_merge_real_time_db
from .analyzer import DBPool
from .dbpreprocess import get_user_list, get_recent_user_list, wxid2userinfo, ParsingMSG, ParsingMicroMsg, \
    ParsingMediaMSG, ParsingOpenIMContact, ParsingFavorite
from .server import start_falsk
import os, json

try:
    VERSION_LIST_PATH = os.path.join(os.path.dirname(__file__), "version_list.json")
    with open(VERSION_LIST_PATH, "r", encoding="utf-8") as f:
        VERSION_LIST = json.load(f)
except:
    VERSION_LIST = {}
    VERSION_LIST_PATH = None

# PYWXDUMP_ROOT_PATH = os.path.dirname(__file__)
# db_init = DBPool("DBPOOL_INIT")

__version__ = "3.0.35"
