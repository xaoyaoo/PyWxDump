# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         main.py.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/14
# -------------------------------------------------------------------------------
import argparse
import sys
import time

from pywxdump import *
import pywxdump

wxdump_ascii = r"""
██████╗ ██╗   ██╗██╗    ██╗██╗  ██╗██████╗ ██╗   ██╗███╗   ███╗██████╗ 
██╔══██╗╚██╗ ██╔╝██║    ██║╚██╗██╔╝██╔══██╗██║   ██║████╗ ████║██╔══██╗
██████╔╝ ╚████╔╝ ██║ █╗ ██║ ╚███╔╝ ██║  ██║██║   ██║██╔████╔██║██████╔╝
██╔═══╝   ╚██╔╝  ██║███╗██║ ██╔██╗ ██║  ██║██║   ██║██║╚██╔╝██║██╔═══╝ 
██║        ██║   ╚███╔███╔╝██╔╝ ██╗██████╔╝╚██████╔╝██║ ╚═╝ ██║██║     
╚═╝        ╚═╝    ╚══╝╚══╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝     
"""
PYWXDUMP_VERSION = pywxdump.__version__

models = {}


def create_parser():
    class CustomArgumentParser(argparse.ArgumentParser):
        def format_help(self):
            # 首先显示软件简介
            # 定义软件简介文本并进行格式化
            line_len = 70
            PYWXDUMP_VERSION = pywxdump.__version__
            wxdump_line = '\n'.join([f'\033[36m{line:^{line_len}}\033[0m' for line in wxdump_ascii.split('\n') if line])
            first_line = f'\033[36m{" PyWxDump v" + PYWXDUMP_VERSION + " ":=^{line_len}}\033[0m'
            brief = 'PyWxDump功能：获取账号信息、解密数据库、查看聊天记录、导出聊天记录为html等'
            other = '更多详情请查看: \033[4m\033[1mhttps://github.com/xaoyaoo/PyWxDump\033[0m'

            separator = f'\033[36m{" options ":-^{line_len}}\033[0m'

            # 获取帮助信息并添加到软件简介下方
            help_text = super().format_help().strip()

            return f'\n{wxdump_line}\n\n{first_line}\n{brief}\n{separator}\n{help_text}\n{separator}\n{other}\n{first_line}\n'

    # 创建命令行参数解析器
    parser = CustomArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-V', '--version', action='version', version=f"PyWxDump v{PYWXDUMP_VERSION}")

    # 添加子命令解析器
    subparsers = parser.add_subparsers(dest="mode", help="""运行模式:""", required=True, metavar="mode")

    return parser, subparsers


main_parser, sub_parsers = create_parser()


class SubMainMetaclass(type):

    def is_implemented_method(cls, name: str, method: str):
        if not hasattr(cls, method) or not callable(getattr(cls, method)):
            raise NotImplementedError("{} NotImplemented [{}]".format(name, method))

    def __init__(cls, name, bases, kwargs):
        super(SubMainMetaclass, cls).__init__(name, bases, kwargs)

        if name in ["BaseSubMainClass"]:
            return

        mode = getattr(cls, "mode")
        if mode in models:
            raise TypeError("mode[{}] is used...".format(mode))

        cls.is_implemented_method(name, "init_parses")
        cls.is_implemented_method(name, "run")

        c = cls()
        models[mode] = c
        c.init_parses(sub_parsers.add_parser(mode, **getattr(c, "parser_kwargs")))


class BaseSubMainClass(metaclass=SubMainMetaclass):
    parser_kwargs = {}

    @property
    def mode(self) -> str:
        raise NotImplementedError()

    def init_parses(self, parser):
        raise NotImplementedError()

    def run(self, args: argparse.Namespace):
        raise NotImplementedError()


class MainBiasAddr(BaseSubMainClass):
    mode = "bias"
    parser_kwargs = {"help": "获取微信基址偏移"}

    def init_parses(self, parser):
        # 添加 'bias_addr' 子命令解析器
        parser.add_argument("--mobile", type=str, help="手机号", metavar="", required=True)
        parser.add_argument("--name", type=str, help="微信昵称", metavar="", required=True)
        parser.add_argument("--account", type=str, help="微信账号", metavar="", required=True)
        parser.add_argument("--key", type=str, metavar="", help="(可选)密钥")
        parser.add_argument("--db_path", type=str, metavar="", help="(可选)已登录账号的微信文件夹路径")
        parser.add_argument("-vlp", '--version_list_path', type=str, metavar="",
                            help="(可选)微信版本偏移文件路径,如有，则自动更新",
                            default=None)

        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
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


class MainWxInfo(BaseSubMainClass):
    mode = "info"
    parser_kwargs = {"help": "获取微信信息"}

    def init_parses(self, parser):
        # 添加 'wx_info' 子命令解析器
        parser.add_argument("-vlp", '--version_list_path', metavar="", type=str,
                            help="(可选)微信版本偏移文件路径", default=VERSION_LIST_PATH)
        parser.add_argument("-s", '--save_path', metavar="", type=str, help="(可选)保存路径【json文件】")
        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
        # 读取微信各版本偏移
        path = args.version_list_path
        save_path = args.save_path
        version_list = json.load(open(path, "r", encoding="utf-8"))
        result = read_info(version_list, True, save_path)  # 读取微信信息
        return result


class MainWxDbPath(BaseSubMainClass):
    mode = "db_path"
    parser_kwargs = {"help": "获取微信文件夹路径"}

    def init_parses(self, parser):
        # 添加 'wx_db_path' 子命令解析器
        parser.add_argument("-r", "--require_list", type=str,
                            help="(可选)需要的数据库名称(eg: -r MediaMSG;MicroMsg;FTSMSG;MSG;Sns;Emotion )",
                            default="all", metavar="")
        parser.add_argument("-wf", "--wx_files", type=str, help="(可选)'WeChat Files'路径", default=None,
                            metavar="")
        parser.add_argument("-id", "--wxid", type=str, help="(可选)wxid_,用于确认用户文件夹",
                            default=None, metavar="")
        return parser

    def run(self, args):
        # 从命令行参数获取值
        require_list = args.require_list
        msg_dir = args.wx_files
        wxid = args.wxid

        user_dirs = get_wechat_db(require_list, msg_dir, wxid, True)  # 获取微信数据库路径
        return user_dirs


class MainDecrypt(BaseSubMainClass):
    mode = "decrypt"
    parser_kwargs = {"help": "解密微信数据库"}

    def init_parses(self, parser):
        # 添加 'decrypt' 子命令解析器
        parser.add_argument("-k", "--key", type=str, help="密钥", required=True, metavar="")
        parser.add_argument("-i", "--db_path", type=str, help="数据库路径(目录or文件)", required=True, metavar="")
        parser.add_argument("-o", "--out_path", type=str, default=os.path.join(os.getcwd(), "decrypted"),
                            help="输出路径(必须是目录)[默认为当前路径下decrypted文件夹]", required=False,
                            metavar="")
        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
        # 从命令行参数获取值
        key = args.key
        db_path = args.db_path
        out_path = args.out_path

        if not os.path.exists(db_path):
            print(f"[-] 数据库路径不存在：{db_path}")
            return

        if not os.path.exists(out_path):
            os.makedirs(out_path)
            print(f"[+] 创建输出文件夹：{out_path}")

        # 调用 decrypt 函数，并传入参数
        result = batch_decrypt(key, db_path, out_path, True)
        return result


class MainMerge(BaseSubMainClass):
    mode = "merge"
    parser_kwargs = {"help": "[测试功能]合并微信数据库(MSG.db or MediaMSG.db)"}

    def init_parses(self, parser):
        # 添加 'decrypt' 子命令解析器
        parser.add_argument("-i", "--db_path", type=str, help="数据库路径(文件路径，使用英文[,]分割)", required=True,
                            metavar="")
        parser.add_argument("-o", "--out_path", type=str, default=os.path.join(os.getcwd(), "decrypted"),
                            help="输出路径(目录或文件名)[默认为当前路径下decrypted文件夹下merge_***.db]",
                            required=False,
                            metavar="")
        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
        # 从命令行参数获取值
        db_path = args.db_path
        out_path = args.out_path

        db_path = db_path.split(",")
        db_path = [i.strip() for i in db_path]
        dbpaths = []
        for i in db_path:
            if not os.path.exists(i):  # 判断路径是否存在
                print(f"[-] 数据库路径不存在：{i}")
                return
            if os.path.isdir(i):  # 如果是文件夹，则获取文件夹下所有的db文件
                dbpaths += [os.path.join(i, j) for j in os.listdir(i) if j.endswith(".db")]
            else:  # 如果是文件，则直接添加
                dbpaths.append(i)

        if (not out_path.endswith(".db")) and (not os.path.exists(out_path)):
            os.makedirs(out_path)
            print(f"[+] 创建输出文件夹：{out_path}")

        print(f"[*] 合并中...（用时较久，耐心等待）")

        result = merge_db(dbpaths, out_path)

        print(f"[+] 合并完成：{result}")
        return result


class MainShowChatRecords(BaseSubMainClass):
    mode = "dbshow"
    parser_kwargs = {"help": "聊天记录查看"}

    def init_parses(self, parser):
        # 添加 'decrypt' 子命令解析器
        parser.add_argument("-merge", "--merge_path", type=str, help="解密后的 merge_all.db 的路径", required=False,
                            metavar="")

        parser.add_argument("-msg", "--msg_path", type=str, help="解密后的 MSG.db 的路径", required=False,
                            metavar="")
        parser.add_argument("-micro", "--micro_path", type=str, help="解密后的 MicroMsg.db 的路径", required=False,
                            metavar="")
        parser.add_argument("-media", "--media_path", type=str, help="解密后的 MediaMSG.db 的路径", required=False,
                            metavar="")

        parser.add_argument("-wid", "--wx_path", type=str,
                            help="(可选)微信文件夹的路径（用于显示图片）", required=False,
                            metavar="")
        parser.add_argument("-myid", "--my_wxid", type=str, help="(可选)微信账号(本人微信id)", required=False,
                            default="wxid_vzzcn5fevion22", metavar="")
        parser.add_argument("--online", action='store_true', help="(可选)是否在线查看(局域网查看)", required=False,
                            default=False)
        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
        # (merge)和(msg_path,micro_path,media_path) 二选一
        if not args.merge_path and not (args.msg_path and args.micro_path and args.media_path):
            print("[-] 请输入数据库路径（[merge_path] or [msg_path, micro_path, media_path]）")
            return

        # 从命令行参数获取值
        merge_path = args.merge_path
        if merge_path:
            args.msg_path = merge_path
            args.micro_path = merge_path
            args.media_path = merge_path

        online = args.online

        if not os.path.exists(args.msg_path) or not os.path.exists(args.micro_path) or not os.path.exists(
                args.media_path):
            print("[-] 输入数据库路径不存在")
            return

        start_falsk(msg_path=args.msg_path, micro_path=args.micro_path, media_path=args.media_path,
                    wx_path=args.wx_path, key="", my_wxid=args.my_wxid, online=online)


class MainExportChatRecords(BaseSubMainClass):
    mode = "export"
    parser_kwargs = {"help": "聊天记录导出为html"}

    def init_parses(self, parser):
        # 添加 'decrypt' 子命令解析器
        parser.add_argument("-u", "--username", type=str, help="微信账号(聊天对象账号)", required=True, metavar="")
        parser.add_argument("-o", "--outpath", type=str, help="导出路径", required=True, metavar="")
        parser.add_argument("-msg", "--msg_path", type=str, help="解密后的 MSG.db 的路径", required=True,
                            metavar="")
        parser.add_argument("-micro", "--micro_path", type=str, help="解密后的 MicroMsg.db 的路径", required=True,
                            metavar="")
        parser.add_argument("-media", "--media_path", type=str, help="解密后的 MediaMSG.db 的路径", required=True,
                            metavar="")
        parser.add_argument("-fs", "--filestorage_path", type=str,
                            help="(可选)文件夹FileStorage的路径（用于显示图片）", required=False, metavar="")
        parser.add_argument("-t", "--type", type=str, help="导出类型(可选:html,csv)", required=False,
                            default="html", metavar="")
        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
        # 从命令行参数获取值
        t = args.type

        if t == "csv":
            try:
                code, ret = export_csv(args.username, args.outpath, args.msg_path, page_size=10000000)
                if not code:
                    print(ret)
                    return
                print(f"[+] {ret}")
                return
            except Exception as e:
                print(e)
                print("[-] 导出失败")
                return
        elif t == "html":
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
        else:
            print("[-] 未知的导出类型")
            return


class MainAll(BaseSubMainClass):
    mode = "all"
    parser_kwargs = {"help": "获取微信信息，解密微信数据库，查看聊天记录"}

    def init_parses(self, parser):
        # 添加 'all' 子命令解析器
        parser.add_argument("-s", '--save_path', metavar="", type=str, help="(可选)wx_info保存路径【json文件】")
        parser.add_argument("--online", action='store_true', help="(可选)是否在线查看(局域网查看)", default=False)
        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
        # 获取微信信息
        save_path = args.save_path
        online = args.online
        WxInfo = read_info(VERSION_LIST, True, save_path)
        if isinstance(WxInfo, str):  # 如果返回的是字符串，则表示出错
            return
        for user in WxInfo:
            key = user.get("key", "")
            if not key:
                print("[-] 未获取到密钥")
                return
            wxid = user.get("wxid", None)
            filePath = user.get("filePath", None)

            WxDbPath = get_wechat_db('all', None, wxid=wxid, is_logging=True)  # 获取微信数据库路径
            if isinstance(WxDbPath, str):  # 如果返回的是字符串，则表示出错
                print(WxDbPath)
                return
            wxdbpaths = [path for user_dir in WxDbPath.values() for paths in user_dir.values() for path in paths]
            if len(wxdbpaths) == 0:
                print("[-] 未获取到数据库路径")
                return

            wxdbpaths = [i for i in wxdbpaths if "Backup.db" not in i and "xInfo.db" not in i]  # 过滤掉无需解密的数据库
            wxdbpaths = [i for i in wxdbpaths if "MicroMsg" in i or "MediaMSG" in i or r"Multi\MSG" in i]  # 过滤掉无需解密的数据库
            wxdblen = len(wxdbpaths)
            print(f"[+] 共发现 {wxdblen} 个微信数据库")
            print("=" * 32)

            decrypted_path = os.path.join(os.getcwd(), "decrypted")
            print(f"[*] 解密后文件夹：{decrypted_path} ")
            print(f"[*] 解密中...（用时较久，耐心等待）")

            # 判断out_path是否为空目录
            if os.path.exists(decrypted_path) and os.listdir(decrypted_path):
                isdel = input(f"[*] 输出文件夹不为空({decrypted_path})\n    是否删除?(y/n):")
                if isdel.lower() == 'y' or isdel.lower() == 'yes':
                    for root, dirs, files in os.walk(decrypted_path, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))

            out_path = os.path.join(decrypted_path, wxid) if wxid else decrypted_path
            if not os.path.exists(out_path):
                os.makedirs(out_path)

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
            if len(errors) > 0:
                print("-" * 32)
                print(
                    "[-] " + f"警告：共 {len(errors)} 个文件未解密(可能原因:非当前登录用户数据库;非加密数据库),详见{out_path}下‘未解密.txt’;")
            # print("; ".join([f'"{wxdbpaths[i]}"' for i in errors]))
            with open(os.path.join(out_path, "未解密.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join([f'{i}' for i in errors]))
            print("=" * 32)

            if len(out_dbs) <= 0:
                print("[-] 未获取到解密后的数据库路径")
                return

            parpare_merge_db_path = [i for i in out_dbs if "de_MicroMsg" in i or "de_MediaMSG" in i or "de_MSG" in i]
            # 合并所有的数据库
            print(f"[*] 合并数据库中...（用时较久，耐心等待）")
            merge_save_path = merge_db(parpare_merge_db_path, os.path.join(out_path, "merge_all.db"))
            time.sleep(1)
            print(f"[+] 合并完成：{merge_save_path}")
            print("=" * 32)
            # # 查看聊天记录
            args.merge_path = merge_save_path
            args.msg_path = merge_save_path
            args.micro_path = merge_save_path
            args.media_path = merge_save_path
            args.wx_path = filePath
            args.my_wxid = wxid
            args.online = online
            MainShowChatRecords().run(args)


class MainUi(BaseSubMainClass):
    mode = "ui"
    parser_kwargs = {"help": "启动UI界面"}

    def init_parses(self, parser):
        # 添加 'ui' 子命令解析器
        parser.add_argument("-p", '--port', metavar="", type=int, help="(可选)端口号", default=5000)
        parser.add_argument("--online", help="(可选)是否在线查看(局域网查看)", default=False, action='store_true')
        parser.add_argument("--debug", help="(可选)是否开启debug模式", default=False, action='store_true')
        parser.add_argument("--openBrowser", help="(可选)是否自动打开浏览器", default=True, action='store_true')
        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
        # 从命令行参数获取值
        online = args.online
        port = args.port
        debug = args.debug
        isopenBrowser = args.openBrowser

        start_falsk(port=port, online=online, debug=debug, isopenBrowser=isopenBrowser)


class MainApi(BaseSubMainClass):
    mode = "api"
    parser_kwargs = {"help": "启动api"}

    def init_parses(self, parser):
        # 添加 'api' 子命令解析器
        parser.add_argument("-p", '--port', metavar="", type=int, help="(可选)端口号", default=5000)
        parser.add_argument("--online", help="(可选)是否在线查看(局域网查看)", default=False, action='store_true')
        parser.add_argument("--debug", action='store_true', help="(可选)是否开启debug模式", default=False)
        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
        # 从命令行参数获取值
        online = args.online
        port = args.port
        debug = args.debug

        start_falsk(port=port, online=online, debug=debug, isopenBrowser=False)


def console_run():
    # 检查是否需要显示帮助信息
    if len(sys.argv) == 1:
        sys.argv.append(MainUi.mode)
    elif len(sys.argv) == 2 and sys.argv[1] not in models.keys():
        sys.argv.append('-h')
        main_parser.print_help()
        return

    args = main_parser.parse_args()  # 解析命令行参数

    if not any(vars(args).values()):
        main_parser.print_help()
        return

    # 根据不同的 'mode' 参数，执行不同的操作
    models[args.mode].run(args)


if __name__ == '__main__':
    console_run()
