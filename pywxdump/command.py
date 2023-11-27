# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         main.py.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/14
# -------------------------------------------------------------------------------
import argparse
import importlib.metadata
import sys
import textwrap

from pywxdump import *


# version_list_path = os.path.join(os.path.dirname(__file__), "version_list.json")


class MainBiasAddr():
    def init_parses(self, parser):
        self.mode = "bias"
        # 添加 'bias_addr' 子命令解析器
        sb_bias_addr = parser.add_parser(self.mode, help="获取微信基址偏移")
        sb_bias_addr.add_argument("--mobile", type=str, help="手机号", metavar="", required=True)
        sb_bias_addr.add_argument("--name", type=str, help="微信昵称", metavar="", required=True)
        sb_bias_addr.add_argument("--account", type=str, help="微信账号", metavar="", required=True)
        sb_bias_addr.add_argument("--key", type=str, metavar="", help="(可选)密钥")
        sb_bias_addr.add_argument("--db_path", type=str, metavar="", help="(可选)已登录账号的微信文件夹路径")
        sb_bias_addr.add_argument("-vlp", '--version_list_path', type=str, metavar="",
                                  help="(可选)微信版本偏移文件路径,如有，则自动更新",
                                  default=None)
        self.sb_bias_addr = sb_bias_addr
        return sb_bias_addr

    def run(self, args):
        # 判断是否至少输入一个参数
        # if not args.key and not args.db_path:
        #     self.sb_bias_addr.error("必须至少指定 --key 或 --db_path 参数中的一个")

        # 从命令行参数获取值
        mobile = args.mobile
        name = args.name
        account = args.account
        key = args.key
        db_path = args.db_path
        vlp = args.version_list_path
        # 调用 run 函数，并传入参数
        rdata = BiasAddr(account, mobile, name, key, db_path).run(True, vlp)
        return rdata


class MainWxInfo():
    def init_parses(self, parser):
        self.mode = "info"
        # 添加 'wx_info' 子命令解析器
        sb_wx_info = parser.add_parser(self.mode, help="获取微信信息")
        sb_wx_info.add_argument("-vlp", '--version_list_path', metavar="", type=str,
                                help="(可选)微信版本偏移文件路径", default=VERSION_LIST_PATH)
        return sb_wx_info

    def run(self, args):
        # 读取微信各版本偏移
        path = args.version_list_path
        version_list = json.load(open(path, "r", encoding="utf-8"))
        result = read_info(version_list, True)  # 读取微信信息
        return result


class MainWxDbPath():
    def init_parses(self, parser):
        self.mode = "db_path"
        # 添加 'wx_db_path' 子命令解析器
        sb_wx_db_path = parser.add_parser(self.mode, help="获取微信文件夹路径")
        sb_wx_db_path.add_argument("-r", "--require_list", type=str,
                                   help="(可选)需要的数据库名称(eg: -r MediaMSG;MicroMsg;FTSMSG;MSG;Sns;Emotion )",
                                   default="all", metavar="")
        sb_wx_db_path.add_argument("-wf", "--wx_files", type=str, help="(可选)'WeChat Files'路径", default=None,
                                   metavar="")
        sb_wx_db_path.add_argument("-id", "--wxid", type=str, help="(可选)wxid_,用于确认用户文件夹",
                                   default=None, metavar="")
        return sb_wx_db_path

    def run(self, args):
        # 从命令行参数获取值
        require_list = args.require_list
        msg_dir = args.wx_files
        wxid = args.wxid

        user_dirs = get_wechat_db(require_list, msg_dir, wxid, True)  # 获取微信数据库路径
        return user_dirs


class MainDecrypt():
    def init_parses(self, parser):
        self.mode = "decrypt"
        # 添加 'decrypt' 子命令解析器
        sb_decrypt = parser.add_parser(self.mode, help="解密微信数据库")
        sb_decrypt.add_argument("-k", "--key", type=str, help="密钥", required=True, metavar="")
        sb_decrypt.add_argument("-i", "--db_path", type=str, help="数据库路径(目录or文件)", required=True, metavar="")
        sb_decrypt.add_argument("-o", "--out_path", type=str, default=os.path.join(os.getcwd(), "decrypted"),
                                help="输出路径(必须是目录)[默认为当前路径下decrypted文件夹]", required=False,
                                metavar="")
        return sb_decrypt

    def run(self, args):
        # 从命令行参数获取值
        key = args.key
        db_path = args.db_path
        out_path = args.out_path

        if not os.path.exists(db_path):
            print("[-] 数据库路径不存在")
            return

        if not os.path.exists(out_path):
            os.makedirs(out_path)
            print(f"[+] 创建输出文件夹：{out_path}")

        # 调用 decrypt 函数，并传入参数
        result = batch_decrypt(key, db_path, out_path, True)
        return result


class MainShowChatRecords():
    def init_parses(self, parser):
        self.mode = "dbshow"
        # 添加 'decrypt' 子命令解析器
        sb_decrypt = parser.add_parser(self.mode, help="聊天记录查看[需要安装flask]")
        sb_decrypt.add_argument("-msg", "--msg_path", type=str, help="解密后的 MSG.db 的路径", required=True,
                                metavar="")
        sb_decrypt.add_argument("-micro", "--micro_path", type=str, help="解密后的 MicroMsg.db 的路径", required=True,
                                metavar="")
        sb_decrypt.add_argument("-media", "--media_path", type=str, help="解密后的 MediaMSG.db 的路径", required=True,
                                metavar="")
        sb_decrypt.add_argument("-fs", "--filestorage_path", type=str,
                                help="(可选)文件夹FileStorage的路径（用于显示图片）", required=False,
                                metavar="")
        return sb_decrypt

    def run(self, args):
        # 从命令行参数获取值
        try:
            from flask import Flask, request, jsonify, render_template, g
            import logging
        except Exception as e:
            print(e)
            print("[-] 请安装flask( pip install flask )")
            return

        if not os.path.exists(args.msg_path) or not os.path.exists(args.micro_path) or not os.path.exists(
                args.media_path):
            print(os.path.exists(args.msg_path), os.path.exists(args.micro_path), os.path.exists(args.media_path))
            print("[-] 输入数据库路径不存在")
            return

        app = Flask(__name__, template_folder='./show_chat/templates')
        app.logger.setLevel(logging.ERROR)

        @app.before_request
        def before_request():

            g.MSG_ALL_db_path = args.msg_path
            g.MicroMsg_db_path = args.micro_path
            g.MediaMSG_all_db_path = args.media_path
            g.FileStorage_path = args.filestorage_path
            g.USER_LIST = get_user_list(args.msg_path, args.micro_path)

        app.register_blueprint(app_show_chat)

        print("[+] 请使用浏览器访问 http://127.0.0.1:5000/ 查看聊天记录")
        app.run(debug=False)


class MainExportChatRecords():
    def init_parses(self, parser):
        self.mode = "export"
        # 添加 'decrypt' 子命令解析器
        sb_decrypt = parser.add_parser(self.mode, help="聊天记录导出为html[需要安装flask]")
        sb_decrypt.add_argument("-u", "--username", type=str, help="微信账号(聊天对象账号)", required=True, metavar="")
        sb_decrypt.add_argument("-o", "--outpath", type=str, help="导出路径", required=True, metavar="")
        sb_decrypt.add_argument("-msg", "--msg_path", type=str, help="解密后的 MSG.db 的路径", required=True,
                                metavar="")
        sb_decrypt.add_argument("-micro", "--micro_path", type=str, help="解密后的 MicroMsg.db 的路径", required=True,
                                metavar="")
        sb_decrypt.add_argument("-media", "--media_path", type=str, help="解密后的 MediaMSG.db 的路径", required=True,
                                metavar="")
        sb_decrypt.add_argument("-fs", "--filestorage_path", type=str,
                                help="(可选)文件夹FileStorage的路径（用于显示图片）", required=False,
                                metavar="")
        return sb_decrypt

    def run(self, args):
        # 从命令行参数获取值
        try:
            from flask import Flask, request, jsonify, render_template, g
            import logging
        except Exception as e:
            print(e)
            print("[-] 请安装flask( pip install flask)")
            return

        if not os.path.exists(args.msg_path) or not os.path.exists(args.micro_path) or not os.path.exists(
                args.media_path):
            print(os.path.exists(args.msg_path), os.path.exists(args.micro_path), os.path.exists(args.media_path))
            print("[-] 输入数据库路径不存在")
            return

        if not os.path.exists(args.outpath):
            os.makedirs(args.outpath)
            print(f"[+] 创建输出文件夹：{args.outpath}")

        export(args.username, args.outpath, args.msg_path, args.micro_path, args.media_path, args.filestorage_path)
        print(f"[+] 导出成功{args.outpath}")


class MainAll():
    def init_parses(self, parser):
        self.mode = "all"
        # 添加 'all' 子命令解析器
        sb_all = parser.add_parser(self.mode, help="获取微信信息，解密微信数据库，查看聊天记录")
        return sb_all

    def run(self, args):
        # 获取微信信息
        WxInfo = read_info(VERSION_LIST, True)

        for user in WxInfo:
            key = user.get("key", "")
            if not key:
                print("[-] 未获取到密钥")
                return
            wxid = user.get("wxid", None)

            WxDbPath = get_wechat_db('all', None, wxid=wxid, is_logging=True)  # 获取微信数据库路径

            wxdbpaths = [path for user_dir in WxDbPath.values() for paths in user_dir.values() for path in paths]
            if len(wxdbpaths) == 0:
                print("[-] 未获取到数据库路径")
                return

            wxdblen = len(wxdbpaths)
            print(f"[+] 共发现 {wxdblen} 个微信数据库")
            print("=" * 32)

            out_path = os.path.join(os.getcwd(), "decrypted", wxid) if wxid else os.path.join(os.getcwd(), "decrypted")
            print(f"[*] 解密后文件夹：{out_path} ")
            print(f"[*] 解密中...（用时较久，耐心等待）")
            if not os.path.exists(out_path):
                os.makedirs(out_path)

            # 判断out_path是否为空目录
            if os.listdir(out_path):
                isdel = input(f"[*] 输出文件夹不为空({out_path})\n    是否删除?(y/n):")
                if isdel.lower() == 'y' or isdel.lower() == 'yes':
                    for root, dirs, files in os.walk(out_path, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))

            # 调用 decrypt 函数，并传入参数   # 解密
            code, ret = batch_decrypt(key, wxdbpaths, out_path, False)
            if not code:
                print(ret)
                return
            print("[+] 解密完成")
            print("-" * 32)
            errors = []
            out_dbs = []
            for code1, ret1 in ret:
                if code1 == False:
                    errors.append(ret1)
                else:
                    print(
                        f'[+] success "{os.path.relpath(ret1[0], os.path.commonprefix(wxdbpaths))}" -> "{os.path.relpath(ret1[1], os.getcwd())}"')
                    out_dbs.append(ret1[1])
            print("-" * 32)
            print(
                "[-] " + f"共 {len(errors)} 个文件解密失败(可能原因:非当前登录用户数据库;非加密数据库),详见{out_path}下‘解密失败.txt’;")
            # print("; ".join([f'"{wxdbpaths[i]}"' for i in errors]))
            with open(os.path.join(out_path, "解密失败.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join([f'{i}' for i in errors]))
            print("=" * 32)

            if len(out_dbs) <= 0:
                print("[-] 未获取到解密后的数据库路径")
                return

            user_path = out_dbs[0].split("MSG")
            FileStorage_path = os.path.join(user_path[0], "FileStorage")

            # 查看聊天记录
            MSGDB = [i for i in out_dbs if "de_MSG" in i]
            MSGDB = MSGDB[-1] if MSGDB else None
            MicroMsgDB = [i for i in out_dbs if "de_MicroMsg" in i]
            MicroMsgDB = MicroMsgDB[-1] if MicroMsgDB else None
            MediaMSGDB = [i for i in out_dbs if "de_MediaMSG" in i]
            MediaMSGDB = MediaMSGDB[-1] if MediaMSGDB else None

            args.msg_path = MSGDB
            args.micro_path = MicroMsgDB
            args.media_path = MediaMSGDB
            args.filestorage_path = FileStorage_path
            MainShowChatRecords().run(args)


PYWXDUMP_VERSION = importlib.metadata.version('pywxdump')


class CustomArgumentParser(argparse.ArgumentParser):
    def format_help(self):
        # 首先显示软件简介
        # 定义软件简介文本并进行格式化
        PYWXDUMP_VERSION = importlib.metadata.version('pywxdump')
        first_line = f'\033[36m{" PyWxDump v" + PYWXDUMP_VERSION + " ":=^80}\033[0m'
        brief = 'PyWxDump是一款用于获取账号信息(昵称/账号/手机/邮箱/数据库密钥)、解密数据库、查看\n聊天记录、备份导出聊天记录为html的工具。'
        other = '更多详情请查看: \033[4m\033[1mhttps://github.com/xaoyaoo/PyWxDump\033[0m'

        separator = f'{"options":-^80}'

        # 获取帮助信息并添加到软件简介下方
        help_text = super().format_help().strip()

        return f'{first_line}\n{brief}\n{separator}\n{help_text}\n{separator}\n{other}\n{first_line}\n'


def console_run():
    # 创建命令行参数解析器
    parser = CustomArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    PYWXDUMP_VERSION = importlib.metadata.version('pywxdump')
    parser.add_argument('-V', '--version', action='version', version=f"PyWxDump v{PYWXDUMP_VERSION}")

    # 添加子命令解析器
    subparsers = parser.add_subparsers(dest="mode", help="""运行模式:""", required=True, metavar="mode")

    modes = {}
    # 添加 'bias' 子命令解析器
    main_bias_addr = MainBiasAddr()
    sb_bias_addr = main_bias_addr.init_parses(subparsers)
    modes[main_bias_addr.mode] = main_bias_addr

    # 添加 'info' 子命令解析器
    main_wx_info = MainWxInfo()
    sb_wx_info = main_wx_info.init_parses(subparsers)
    modes[main_wx_info.mode] = main_wx_info

    # 添加 'db_path' 子命令解析器
    main_wx_db_path = MainWxDbPath()
    sb_wx_db_path = main_wx_db_path.init_parses(subparsers)
    modes[main_wx_db_path.mode] = main_wx_db_path

    # 添加 'decrypt' 子命令解析器
    main_decrypt = MainDecrypt()
    sb_decrypt = main_decrypt.init_parses(subparsers)
    modes[main_decrypt.mode] = main_decrypt

    # 添加 '' 子命令解析器
    main_show_chat_records = MainShowChatRecords()
    sb_dbshow = main_show_chat_records.init_parses(subparsers)
    modes[main_show_chat_records.mode] = main_show_chat_records

    # 添加 'export' 子命令解析器
    main_export_chat_records = MainExportChatRecords()
    sb_export = main_export_chat_records.init_parses(subparsers)
    modes[main_export_chat_records.mode] = main_export_chat_records

    # 添加 'all' 子命令解析器
    main_all = MainAll()
    sb_all = main_all.init_parses(subparsers)
    modes[main_all.mode] = main_all

    # 检查是否需要显示帮助信息
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    elif len(sys.argv) == 2 and sys.argv[1] in modes.keys() and sys.argv[1] not in [main_all.mode, main_wx_info.mode,
                                                                                    main_wx_db_path.mode]:
        sys.argv.append('-h')

    args = parser.parse_args()  # 解析命令行参数

    if not any(vars(args).values()):
        parser.print_help()

    # 根据不同的 'mode' 参数，执行不同的操作
    modes[args.mode].run(args)


if __name__ == '__main__':
    console_run()
