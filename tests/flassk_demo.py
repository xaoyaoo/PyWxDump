# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         flassk_demo.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/12/11
# -------------------------------------------------------------------------------
from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/api/demo', methods=["get",'POST'])
def demo():
    # 模拟不同的API情况
    # 0: 请求成功
    r_data = {
        'code': 0,
        'body': {
            'message': 'Success!',
            'data': {
                'key': 'value'
            }
        },
        'msg': 'success',
        'extra': {}
    }
    return jsonify(r_data)

if __name__ == '__main__':
    app.run(debug=True)
