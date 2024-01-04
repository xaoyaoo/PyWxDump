# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         server.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/01/04
# -------------------------------------------------------------------------------
import logging

from flask import Flask,g
from flask_cors import CORS
from pywxdump.api.api import api

app = Flask(__name__, template_folder='./ui/web', static_folder='./ui/web/assets/', static_url_path='/assets/')
app.logger.setLevel(logging.ERROR)


CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # 允许所有域名跨域

@app.before_request
def before_request():
    path = r"****.db"
    g.msg_path = path
    g.micro_path = path
    g.media_path = path
    g.wxid_path = r"*****"
    g.my_wxid = "******"
    g.tmp_path = "dist"  # 临时文件夹,用于存放图片等
    g.user_list = []


app.register_blueprint(api)

print("[+] 请使用浏览器访问 http://127.0.0.1:5000/ 查看聊天记录")
app.run(host='0.0.0.0', port=5000, debug=True)