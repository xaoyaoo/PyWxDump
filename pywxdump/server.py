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

from pywxdump.common.config.oss_config.s3_config import S3Config
from pywxdump.common.config.server_config import ServerConfig


def start_falsk(server_config: ServerConfig):
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
    tmp_path = os.path.join(os.getcwd(), "wxdump_tmp")  # 临时文件夹,用于存放图片等
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
        print(f"[+] 创建临时文件夹：{tmp_path}")

    session_file = os.path.join(tmp_path, "conf.json")  # 用于存放各种基础信息

    from flask import Flask, g
    from flask_cors import CORS
    from pywxdump.api import api, read_session, save_session
    import logging

    # 检查端口是否被占用
    if server_config.online:
        host = '0.0.0.0'
    else:
        host = "127.0.0.1"

    app = Flask(__name__, template_folder='./ui/web', static_folder='./ui/web/assets/', static_url_path='/assets/')
    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True
    # 设置超时时间为 1000 秒
    app.config['TIMEOUT'] = 1000
    app.secret_key = 'secret_key'

    app.logger.setLevel(logging.ERROR)

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

        g.tmp_path = tmp_path  # 临时文件夹,用于存放图片等
        g.sf = session_file  # 用于存放各种基础信息

    wxid = server_config.my_wxid if server_config.my_wxid else "test"
    if server_config.merge_path: save_session(session_file, wxid, "merge_path", server_config.merge_path)
    if server_config.wx_path: save_session(session_file, wxid, "wx_path", server_config.wx_path)
    if server_config.key: save_session(session_file, wxid, "key", server_config.key)
    if server_config.my_wxid: save_session(session_file, wxid, "my_wxid", server_config.my_wxid)
    if server_config.oss_config: save_session(session_file, wxid, "oss_config", server_config.oss_config_to_json())
    if not os.path.exists(session_file):
        save_session(session_file, wxid, "last", server_config.my_wxid)

    app.register_blueprint(api)
    if server_config.is_open_browser:
        try:
            # 自动打开浏览器
            url = f"http://127.0.0.1:{server_config.port}/"
            # 根据操作系统使用不同的命令打开默认浏览器
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.call(['open', url])
            elif sys.platform.startswith('win'):  # Windows
                subprocess.call(['start', url], shell=True)
            elif sys.platform.startswith('linux'):  # Linux
                subprocess.call(['xdg-open', url])
            else:
                print("Unsupported platform, can't open browser automatically.")
        except Exception as e:
            pass

    def is_port_in_use(host, port):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
            except socket.error:
                return True
        return False

    if is_port_in_use(host, server_config.port):
        print(f"Port {server_config.port} is already in use. Choose a different port.")
        input("Press Enter to exit...")
    else:
        time.sleep(1)
        print("[+] 请使用浏览器访问 http://127.0.0.1:5000/ 查看聊天记录")
        app.run(host=host, port=server_config.port, debug=server_config.debug)


if __name__ == '__main__':
    merge_path = r"****.db"

    wx_path = r"****"
    my_wxid = "****"
    server_config = ServerConfig.builder()
    server_config.merge_path("s3://*********-1256220500/*********/merge_all.db")
    server_config.wx_path("s3://*********-1256220500/*********")
    server_config.my_wxid("test")
    server_config.port(9000)
    server_config.online(True)
    server_config.is_open_browser(False)

    s3Config = S3Config("AKIDaAjA*********I1kR4gFdv67v", "wlT2ldSBk*********Qh4fEev47",
                        "https://cos.ap-nanjing.myqcloud.com")
    server_config.oss_config(s3Config)
    start_falsk(server_config.build())

