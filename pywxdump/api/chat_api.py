# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         chat_api.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/01/02
# -------------------------------------------------------------------------------
from flask import Flask, request, render_template, g, Blueprint
from pywxdump import analyzer
from pywxdump.api.rjson import ReJson, RqJson
# from flask_cors import CORS

app = Flask(__name__ , static_folder='../ui/web/dist', static_url_path='/')


@app.route('/api/contact_list', methods=["GET", 'POST'])
def contact_list():
    """
    获取联系人列表
    :return:
    """
    if request.method == "POST":
        # 从header中读取micro_path
        micro_path = request.headers.get("micro_path")
        try:
            # 获取联系人列表
            contact_list = analyzer.get_contact_list(micro_path)
            return ReJson(0, contact_list)
        except Exception as e:
            return ReJson(9999, msg=str(e))
    else:
        return ReJson(9999)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
