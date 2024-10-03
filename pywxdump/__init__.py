# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         __init__.py.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/14
# -------------------------------------------------------------------------------
__version__ = "3.1.34"

import os, json

try:
    WX_OFFS_PATH = os.path.join(os.path.dirname(__file__), "WX_OFFS.json")
    with open(WX_OFFS_PATH, "r", encoding="utf-8") as f:
        WX_OFFS = json.load(f)
except:
    WX_OFFS = {}
    WX_OFFS_PATH = None

from .wx_core import BiasAddr, get_wx_info, get_wx_db, batch_decrypt, decrypt, get_core_db
from .wx_core import merge_db, decrypt_merge, merge_real_time_db, all_merge_real_time_db
from .db import DBHandler, MsgHandler, MicroHandler, MediaHandler, OpenIMContactHandler, FavoriteHandler, \
    PublicMsgHandler
from .api import start_server, gen_fastapi_app
from .api.export import export_html, export_csv, export_json

# PYWXDUMP_ROOT_PATH = os.path.dirname(__file__)
# db_init = DBPool("DBPOOL_INIT")


__all__ = ["BiasAddr", "get_wx_info", "get_wx_db", "batch_decrypt", "decrypt", "get_core_db",
           "merge_db", "decrypt_merge", "merge_real_time_db", "all_merge_real_time_db",
           "DBHandler", "MsgHandler", "MicroHandler", "MediaHandler", "OpenIMContactHandler", "FavoriteHandler",
           "PublicMsgHandler",
           "start_server", "WX_OFFS", "WX_OFFS_PATH", "__version__"]
