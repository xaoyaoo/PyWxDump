import pymem


def get(WXName: str, WXAccount: str, WXMobile: str, WXMail: str = "0", keySkew: int = 64):
    target = {}
    process_name = "WeChat.exe"
    pm = pymem.Pymem(process_name)
    for item in pm.list_modules():
        if item.name == "WeChatWin.dll":
            search_start = item.lpBaseOfDll
            break
    else:
        raise ValueError("未找到dll, 可能微信未运行")
    search_end = 0x00007FFFFFFFFFFF
    print(f"正在寻找: {search_start}-> {search_end}")
    current_address = search_start  # + 65000000
    current_num = 0
    while current_address < search_end:
        try:
            value = pm.read_string(current_address)
            if value == WXMobile:
                print(f"-({WXMobile}){current_address}/{search_end}({current_address - search_start})")
                target["mobile"] = current_address-search_start
                current_num += 1
            elif value == WXName:
                print(f"-({WXName}){current_address}/{search_end}({current_address - search_start})")
                target["name"] = current_address-search_start
                current_num += 1
            elif value == WXAccount:
                target["account"] = current_address-search_start
                print(f"-({WXAccount}){current_address}/{search_end}({current_address-search_start})")
                target["key"] = current_address-search_start-keySkew
                current_num += 1
        except:
            pass
        finally:
            print(
                f"\r正在寻找: {current_address}/{search_end}({hex(current_address - search_start)}|{current_address - search_start}) ->{len(target)}",
                end="")
            if current_num >= 4:
                target["mail"] = 0
                print("")
                break
            current_address += 1
    return target


name = ""
account = ""
mobile = ""
skew = get(name, account, mobile)
print(skew)
