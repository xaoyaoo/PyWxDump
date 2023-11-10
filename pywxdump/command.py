# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         main.py.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/10/14
# -------------------------------------------------------------------------------
import json
import argparse
import os

from . import *


# version_list_path = os.path.join(os.path.dirname(__file__), "version_list.json")


class MainBiasAddr():
    def init_parses(self, parser):
        # 添加 'bias_addr' 子命令解析器
        sb_bias_addr = parser.add_parser("bias_addr", help="获取微信基址偏移")
        sb_bias_addr.add_argument("--mobile", type=str, help="手机号", required=True)
        sb_bias_addr.add_argument("--name", type=str, help="微信昵称", required=True)
        sb_bias_addr.add_argument("--account", type=str, help="微信账号", required=True)
        sb_bias_addr.add_argument("--key", type=str, help="(可选)密钥")
        sb_bias_addr.add_argument("--db_path", type=str, help="(可选)已登录账号的微信文件夹路径")
        sb_bias_addr.add_argument("-vlp", type=str, help="(可选)微信版本偏移文件路径,如有，则自动更新",
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
        vlp = args.vlp
        # 调用 run 函数，并传入参数
        rdata = BiasAddr(account, mobile, name, key, db_path).run()
        print("{版本:微信昵称,微信账号,微信手机号,微信邮箱,微信KEY,微信原始ID(wxid_******)}")
        print(rdata)

        if vlp is not None:
            # 添加到version_list.json
            version_list = json.load(open(vlp, "r", encoding="utf-8"))
            version_list.update(rdata)
            json.dump(version_list, open(vlp, "w", encoding="utf-8"), ensure_ascii=False, indent=4)

        return rdata


class MainWxInfo():
    def init_parses(self, parser):
        # 添加 'wx_info' 子命令解析器
        sb_wx_info = parser.add_parser("wx_info", help="获取微信信息")
        sb_wx_info.add_argument("-vlp", type=str, help="(可选)微信版本偏移文件路径", default=VERSION_LIST_PATH)
        return sb_wx_info

    def run(self, args):
        # 读取微信各版本偏移
        VERSION_LIST_PATH = args.vlp
        version_list = json.load(open(VERSION_LIST_PATH, "r", encoding="utf-8"))
        result = read_info(version_list)  # 读取微信信息

        print("=" * 32)
        if isinstance(result, str):  # 输出报错
            print(result)
        else:  # 输出结果
            for i, rlt in enumerate(result):
                for k, v in rlt.items():
                    print(f"[+] {k:>7}: {v}")
                print(end="-" * 32 + "\n" if i != len(result) - 1 else "")
        print("=" * 32)
        return result


class MainWxDbPath():
    def init_parses(self, parser):
        # 添加 'wx_db_path' 子命令解析器
        sb_wx_db_path = parser.add_parser("wx_db", help="获取微信文件夹路径")
        sb_wx_db_path.add_argument("-r", "--require_list", type=str,
                                   help="(可选)需要的数据库名称(eg: -r MediaMSG;MicroMsg;FTSMSG;MSG;Sns;Emotion )",
                                   default="all", metavar="")
        sb_wx_db_path.add_argument("-wf", "--wx_files", type=str, help="(可选)'WeChat Files'路径", default=None,
                                   metavar="")
        return sb_wx_db_path

    def run(self, args):
        # 从命令行参数获取值
        require_list = args.require_list
        msg_dir = args.wx_files

        user_dirs = get_wechat_db(require_list, msg_dir)

        if isinstance(user_dirs, str):
            print(user_dirs)
        else:
            for user, user_dir in user_dirs.items():
                print(f"[+] {user}")
                for n, paths in user_dir.items():
                    print(f"    {n}:")
                    for path in paths[:2]:
                        print(f"        {path}")
                    if len(paths) > 2:
                        print(f"        ...")
            print("-" * 32)
            print(f"[+] 共 {len(user_dirs)} 个微信账号")

        return user_dirs


class MainDecrypt():
    def init_parses(self, parser):
        # 添加 'decrypt' 子命令解析器
        sb_decrypt = parser.add_parser("decrypt", help="解密微信数据库")
        sb_decrypt.add_argument("-k", "--key", type=str, help="密钥", required=True, metavar="")
        sb_decrypt.add_argument("-i", "--db_path", type=str, help="数据库路径(目录or文件)", required=True, metavar="")
        sb_decrypt.add_argument("-o", "--out_path", type=str,
                                help="输出路径(必须是目录),输出文件为 out_path/de_{original_name}", required=True,
                                metavar="")
        return sb_decrypt

    def run(self, args):
        # 从命令行参数获取值
        key = args.key
        db_path = args.db_path
        out_path = args.out_path

        # 调用 decrypt 函数，并传入参数
        result = batch_decrypt(key, db_path, out_path)
        if isinstance(result, list):
            for i in result:
                if isinstance(i, str):
                    print(i)
                else:
                    print(f'[+] "{i[1]}" -> "{os.path.relpath(i[2], out_path)}"')
        else:
            print(result)


class MainAnalyseWxDb():
    def init_parses(self, parser):
        # 添加 'parse_wx_db' 子命令解析器
        sb_parse_wx_db = parser.add_parser("analyse", help="解析微信数据库(未完成)")
        sb_parse_wx_db.add_argument("--arg", type=str, help="参数")
        return sb_parse_wx_db

    def run(self, args):
        print(f"解析微信数据库（未完成）")


class MainAll():
    def init_parses(self, parser):
        # 添加 'all' 子命令解析器
        sb_all = parser.add_parser("all", help="执行所有操作(除获取基址偏移、Analyse)")
        return sb_all

    def run(self, args):
        # 获取微信信息
        args.vlp = VERSION_LIST_PATH
        result_WxInfo = MainWxInfo().run(args)
        keys = [i.get('key', "") for i in result_WxInfo]
        if not keys:
            print("[-] 未获取到密钥")
            return
        wxids = [i.get('wxid', "") for i in result_WxInfo]

        args.require_list = 'all'
        args.wx_files = None
        result_WxDbPath = MainWxDbPath().run(args)
        wxdbpaths = [path for user_dir in result_WxDbPath.values() for paths in user_dir.values() for path in paths]
        wxdblen = len(wxdbpaths)
        print(f"[+] 共 {wxdblen} 个微信数据库(包含所有本地曾登录的微信)")
        print("=" * 32)

        out_path = os.path.join(os.getcwd(), "decrypted")
        print(f"[*] 解密后文件夹：{out_path} ")
        print(f"[*] 解密中...（用时较久，耐心等待）")
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        rd = {}
        for key in keys:
            rd[key] = batch_decrypt(key, wxdbpaths, out_path)

        result_Decrypt = [None] * wxdblen
        for i in range(wxdblen):
            for k, v in rd.items():
                if isinstance(v[i], list):
                    result_Decrypt[i] = v[i]
                    break
                else:
                    result_Decrypt[i] = v[i]

        print("[+] 解密完成")
        print("-" * 32)

        errors = []
        for i in range(wxdblen):
            if isinstance(result_Decrypt[i], str):
                errors.append(i)
            else:
                print(
                    f'[+] success "{os.path.relpath(result_Decrypt[i][1], os.path.commonprefix(wxdbpaths))}" -> "{os.path.relpath(result_Decrypt[i][2], os.getcwd())}"')
        print("-" * 32)
        print("[-] " + f"共 {len(errors)} 个文件解密失败;")
        # print("; ".join([f'"{wxdbpaths[i]}"' for i in errors]))
        print("=" * 32)


def console_run():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    # 添加子命令解析器
    subparsers = parser.add_subparsers(dest="mode", help="""运行模式:""", required=True, metavar="mode")

    # 添加 'bias_addr' 子命令解析器
    main_bias_addr = MainBiasAddr()
    sb_bias_addr = main_bias_addr.init_parses(subparsers)

    # 添加 'wx_info' 子命令解析器
    main_wx_info = MainWxInfo()
    sb_wx_info = main_wx_info.init_parses(subparsers)

    # 添加 'wx_db_path' 子命令解析器
    main_wx_db_path = MainWxDbPath()
    sb_wx_db_path = main_wx_db_path.init_parses(subparsers)

    # 添加 'decrypt' 子命令解析器
    main_decrypt = MainDecrypt()
    sb_decrypt = main_decrypt.init_parses(subparsers)

    # 添加 'parse_wx_db' 子命令解析器
    main_parse_wx_db = MainAnalyseWxDb()
    sb_parse_wx_db = main_parse_wx_db.init_parses(subparsers)

    # 添加 'all' 子命令解析器
    main_all = MainAll()
    sb_all = main_all.init_parses(subparsers)

    args = parser.parse_args()  # 解析命令行参数

    if not any(vars(args).values()):
        parser.print_help()
    # 根据不同的 'mode' 参数，执行不同的操作
    if args.mode == "bias_addr":
        main_bias_addr.run(args)
    elif args.mode == "wx_info":
        main_wx_info.run(args)
    elif args.mode == "wx_db":
        main_wx_db_path.run(args)
    elif args.mode == "decrypt":
        main_decrypt.run(args)
    elif args.mode == "parse":
        main_parse_wx_db.run(args)
    elif args.mode == "all":
        main_all.run(args)


if __name__ == '__main__':
    console_run()
