# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         server.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/01/04
# -------------------------------------------------------------------------------
import os
import subprocess
import sys
import time
import logging

server_loger = logging.getLogger("server")


def is_port_in_use(_host, _port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((_host, _port))
        except socket.error:
            return True
    return False


def start_falsk(merge_path="", wx_path="", key="", my_wxid="", port=5000, online=False, debug=False,
                isopenBrowser=True):
    """
    启动flask
    :param merge_path:  合并后的数据库路径
    :param wx_path:  微信文件夹的路径（用于显示图片）
    :param key:  密钥
    :param my_wxid:  微信账号(本人微信id)
    :param port:  端口号
    :param online:  是否在线查看(局域网查看)
    :param debug:  是否开启debug模式
    :param isopenBrowser:  是否自动打开浏览器
    :return:
    """
    work_path = os.path.join(os.getcwd(), "wxdump_work")  # 临时文件夹,用于存放图片等
    if not os.path.exists(work_path):
        os.makedirs(work_path)
        server_loger.info(f"[+] 创建临时文件夹：{work_path}")
        print(f"[+] 创建临时文件夹：{work_path}")

    conf_auto_file = os.path.join(work_path, "conf_auto.json")  # 用于存放各种基础信息

    from flask import Flask, g
    from flask_cors import CORS
    from pywxdump.api import rs_api, ls_api, get_conf, set_conf

    # 检查端口是否被占用
    if online:
        host = '0.0.0.0'
    else:
        host = "127.0.0.1"

    app = Flask(__name__, template_folder='./ui/web', static_folder='./ui/web/assets/', static_url_path='/assets/')

    # 设置超时时间为 1000 秒
    app.config['TIMEOUT'] = 1000
    app.secret_key = 'secret_key'

    app.logger.setLevel(logging.WARNING)

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # 允许所有域名跨域

    @app.after_request  # 请求后的处理 用于解决部分用户浏览器不支持flask以及vue的js文件返回问题
    def changeHeader(response):
        disposition = response.get_wsgi_headers('environ').get(
            'Content-Disposition') or ''  # 获取返回头文件名描述，如'inline; filename=index.562b9b5a.js'
        if disposition.rfind('.js') == len(disposition) - 3:
            response.mimetype = 'application/javascript'
        return response

    @app.before_request
    def before_request():
        g.work_path = work_path  # 临时文件夹,用于存放图片等-新版本
        g.caf = conf_auto_file  # 用于存放各种基础信息-新版本
        g.at = "auto_setting"  # 用于默认设置-新版本

    if merge_path: set_conf(conf_auto_file, g.at, "merge_path", merge_path)
    if wx_path: set_conf(conf_auto_file, g.at, "wx_path", wx_path)
    if key: set_conf(conf_auto_file, g.at, "key", key)
    if my_wxid: set_conf(conf_auto_file, g.at, "my_wxid", my_wxid)
    if not os.path.exists(conf_auto_file):
        set_conf(conf_auto_file, g.at, "last", my_wxid)

    app.register_blueprint(rs_api)
    app.register_blueprint(ls_api)

    if isopenBrowser:
        try:
            # 自动打开浏览器
            url = f"http://127.0.0.1:{port}/"
            # 根据操作系统使用不同的命令打开默认浏览器
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.call(['open', url])
            elif sys.platform.startswith('win'):  # Windows
                subprocess.call(['start', url], shell=True)
            elif sys.platform.startswith('linux'):  # Linux
                subprocess.call(['xdg-open', url])
            else:
                server_loger.error(f"Unsupported platform, can't open browser automatically.", exc_info=True)
                print("Unsupported platform, can't open browser automatically.")
        except Exception as e:
            server_loger.error(f"自动打开浏览器失败：{e}", exc_info=True)

    if is_port_in_use(host, port):
        server_loger.error(f"Port {port} is already in use. Choose a different port.")
        print(f"Port {port} is already in use. Choose a different port.")
        input("Press Enter to exit...")
    else:
        time.sleep(1)
        server_loger.info(f"启动flask服务，host:port：{host}:{port}")
        print("[+] 请使用浏览器访问 http://127.0.0.1:5000/ 查看聊天记录")
        app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    merge_path = r"****.db"

    wx_path = r"****"
    my_wxid = "****"

    start_falsk(merge_path=merge_path, wx_path=wx_path, my_wxid=my_wxid,
                port=5000, online=False, debug=False, isopenBrowser=False)
