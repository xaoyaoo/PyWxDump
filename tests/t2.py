# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         t2.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/21
# -------------------------------------------------------------------------------
import json

# from pywxdump import VERSION_LIST

with open(r'D:\_code\py_code\test\a2023\b0821wxdb\PyWxDump\pywxdump\version_list.json', 'r') as f:
    VERSION_LIST = json.load(f)

for version in VERSION_LIST:
    VERSION_LIST[version] = VERSION_LIST[version] + [0] if len(VERSION_LIST[version]) == 5 else VERSION_LIST[version]

with open(r'D:\_code\py_code\test\a2023\b0821wxdb\PyWxDump\pywxdump\version_list.json', 'w') as f:
    json.dump(VERSION_LIST, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    pass
