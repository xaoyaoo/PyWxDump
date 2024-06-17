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
    mode = "wx_path"
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
        # 添加 'merge' 子命令解析器
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
        # 添加 'dbshow' 子命令解析器
        parser.add_argument("-merge", "--merge_path", type=str, help="解密并合并后的 merge_all.db 的路径",
                            required=False, metavar="")
        parser.add_argument("-wid", "--wx_path", type=str,
                            help="(可选)微信文件夹的路径（用于显示图片）", required=False,
                            metavar="")
        parser.add_argument("-myid", "--my_wxid", type=str, help="(可选)微信账号(本人微信id)", required=False,
                            default="", metavar="")
        parser.add_argument("--online", action='store_true', help="(可选)是否在线查看(局域网查看)", required=False,
                            default=False)
        # parser.add_argument("-k", "--key", type=str, help="(可选)密钥", required=False, metavar="")
        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
        # (merge)和(msg_path,micro_path,media_path) 二选一
        # if not args.merge_path and not (args.msg_path and args.micro_path and args.media_path):
        #     print("[-] 请输入数据库路径（[merge_path] or [msg_path, micro_path, media_path]）")
        #     return

        # 目前仅能支持merge database
        if not args.merge_path:
            print("[-] 请输入数据库路径（[merge_path]）")
            return

        # 从命令行参数获取值
        merge_path = args.merge_path

        online = args.online

        if not os.path.exists(merge_path):
            print("[-] 输入数据库路径不存在")
            return

        start_falsk(merge_path=merge_path, wx_path=args.wx_path, key="", my_wxid=args.my_wxid, online=online)


class MainExportChatRecords(BaseSubMainClass):
    mode = "export"
    parser_kwargs = {"help": "[已废弃]聊天记录导出为html"}

    def init_parses(self, parser):
        # 添加 'export' 子命令解析器
        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
        print("[+] export命令已废弃，请使用ui命令[wxdump ui]或api命令[wxdump api]启动服务")


class MainAll(BaseSubMainClass):
    mode = "all"
    parser_kwargs = {"help": "[已废弃]获取微信信息，解密微信数据库，查看聊天记录"}

    def init_parses(self, parser):
        # 添加 'all' 子命令解析器
        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
        print("[+] all命令已废弃，请使用ui命令[wxdump ui]或api命令[wxdump api]启动服务")


class MainUi(BaseSubMainClass):
    mode = "ui"
    parser_kwargs = {"help": "启动UI界面"}

    def init_parses(self, parser):
        # 添加 'ui' 子命令解析器
        parser.add_argument("-p", '--port', metavar="", type=int, help="(可选)端口号", default=5000)
        parser.add_argument("--online", help="(可选)是否在线查看(局域网查看)", default=False, action='store_true')
        parser.add_argument("--debug", help="(可选)是否开启debug模式", default=False, action='store_true')
        parser.add_argument("--noOpenBrowser", dest='isOpenBrowser', action='store_false', default=True,
                            help="(可选)用于禁用自动打开浏览器")
        return parser

    def run(self, args):
        print(f"[*] PyWxDump v{pywxdump.__version__}")
        # 从命令行参数获取值
        online = args.online
        port = args.port
        debug = args.debug
        isopenBrowser = args.isOpenBrowser

        start_falsk(port=port, online=online, debug=debug, isopenBrowser=isopenBrowser)


class MainApi(BaseSubMainClass):
    mode = "api"
    parser_kwargs = {"help": "启动api，不打开浏览器"}

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
