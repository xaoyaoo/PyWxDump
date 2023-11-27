# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         __init__.py.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/14
# -------------------------------------------------------------------------------
from .bias_addr.get_bias_addr import BiasAddr
from .wx_info.get_wx_info import read_info
from .wx_info.get_wx_db import get_wechat_db
from .decrypted.decrypt import batch_decrypt, decrypt
from .decrypted.get_wx_decrypted_db import all_decrypt, merge_copy_msg_db, merge_msg_db, merge_media_msg_db
from .analyse.parse import read_img_dat, read_emoji, decompress_CompressContent, read_audio_buf, read_audio, parse_xml_string
from .show_chat import app_show_chat, get_user_list, export

import os,json

VERSION_LIST_PATH = os.path.join(os.path.dirname(__file__), "version_list.json")
with open(VERSION_LIST_PATH, "r", encoding="utf-8") as f:
    VERSION_LIST = json.load(f)
