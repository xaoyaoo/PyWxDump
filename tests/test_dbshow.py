# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         test_dbshow.py
# Description:  显示数据库聊天记录
# Author:       xaoyaoo
# Date:         2023/11/15
# -------------------------------------------------------------------------------
try:
    from flask import Flask, request, jsonify, render_template, g
    import logging
    from pywxdump.show_chat.main_window import app_show_chat, get_user_list
except Exception as e:
    print(e)
    print("[-] 请安装flask( pip install flask )")
    assert "[-] 请安装flask( pip install flask )"

app = Flask(__name__, template_folder='./show_chat/templates')
app.logger.setLevel(logging.ERROR)

msg_path = r"xxxxxx"
micro_path = r"xxxxxx"
media_path = r"xxxxxx"
filestorage_path = r"xxxxxx"

@app.before_request
def before_request():
    g.MSG_ALL_db_path = msg_path
    g.MicroMsg_db_path = micro_path
    g.MediaMSG_all_db_path = media_path
    g.FileStorage_path = filestorage_path
    g.USER_LIST = get_user_list(msg_path, micro_path)


app.register_blueprint(app_show_chat)

print("[+] 请使用浏览器访问 http://127.0.0.1:5000/ 查看聊天记录")
app.run(debug=False)
