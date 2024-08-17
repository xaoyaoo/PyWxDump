# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         __init__.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/12/14
# -------------------------------------------------------------------------------
import os
import subprocess
import sys
import time
import uvicorn

from fastapi import FastAPI, Request, Path, Query
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from .utils import gc, is_port_in_use, server_loger
from .rjson import ReJson
from .remote_server import rs_api
from .local_server import ls_api

from pywxdump import __version__


def gen_fastapi_app():
    app = FastAPI(title="pywxdump", description="微信工具", version=__version__,
                  terms_of_service="https://github.com/xaoyaoo/pywxdump",
                  contact={"name": "xaoyaoo", "url": "https://github.com/xaoyaoo/pywxdump"},
                  license_info={"name": "MIT License", "url": "https://github.com/xaoyaoo/PyWxDump/blob/master/LICENSE"})

    # 跨域
    origins = [
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:8080",  # 开发环境的客户端地址"
        # "http://0.0.0.0:5000",
        # "*"
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # 允许所有源
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有方法
        allow_headers=["*"],  # 允许所有头
    )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        # print(request.body)
        return ReJson(1002, {"detail": exc.errors()})

    @app.get("/")
    @app.get("/index.html")
    async def index():
        response = RedirectResponse(url="/s/index.html", status_code=307)
        return response

    # 路由挂载
    app.include_router(rs_api, prefix='/api/rs', tags=['远程api'])
    app.include_router(ls_api, prefix='/api/ls', tags=['本地api'])

    # 静态文件挂载
    web_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "web")
    if os.path.exists(os.path.join(web_path, "index.html")):
        app.mount("/s", StaticFiles(directory=web_path), name="static")

    return app


def start_server(port=5000, online=False, debug=False, isopenBrowser=True):
    """
    启动flask
    :param port:  端口号
    :param online:  是否在线查看(局域网查看)
    :param debug:  是否开启debug模式
    :param isopenBrowser:  是否自动打开浏览器
    :return:
    """
    # 全局变量
    work_path = os.path.join(os.getcwd(), "wxdump_work")  # 临时文件夹,用于存放图片等
    if not os.path.exists(work_path):
        os.makedirs(work_path)
        server_loger.info(f"[+] 创建临时文件夹：{work_path}")
        print(f"[+] 创建临时文件夹：{work_path}")
    conf_file = os.path.join(work_path, "conf_auto.json")  # 用于存放各种基础信息
    auto_setting = "auto_setting"
    env_file = os.path.join(work_path, ".env")  # 用于存放环境变量
    # set 环境变量
    os.environ["PYWXDUMP_WORK_PATH"] = work_path
    os.environ["PYWXDUMP_CONF_FILE"] = conf_file
    os.environ["PYWXDUMP_AUTO_SETTING"] = auto_setting

    with open(env_file, "w", encoding="utf-8") as f:
        f.write(f"PYWXDUMP_WORK_PATH = '{work_path}'\n")
        f.write(f"PYWXDUMP_CONF_FILE = '{conf_file}'\n")
        f.write(f"PYWXDUMP_AUTO_SETTING = '{auto_setting}'\n")

    # 检查端口是否被占用
    if online:
        host = '0.0.0.0'
    else:
        host = "127.0.0.1"

    if is_port_in_use(host, port):
        server_loger.error(f"Port {port} is already in use. Choose a different port.")
        print(f"Port {port} is already in use. Choose a different port.")
        input("Press Enter to exit...")
        return  # 退出程序
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

    time.sleep(1)
    server_loger.info(f"启动flask服务，host:port：{host}:{port}")
    print("[+] 请使用浏览器访问 http://127.0.0.1:5000/ 查看聊天记录")
    global app
    app = gen_fastapi_app()
    uvicorn.run(app=app, host=host, port=port, reload=debug, log_level="info", workers=1, env_file=env_file)


app = None

__all__ = ["start_server", "gen_fastapi_app"]
