# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         gen_change_log.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/01/21
# -------------------------------------------------------------------------------
import os
import re
import time


def custom_sort_key(tag):
    if tag == 'python':
        return "000.000.000"
    elif tag == 'HEAD':
        return "999.999.999"
    elif tag.startswith('v'):
        tag = tag[1:].split(".")
        tag_dict = {"major": 0, "minor": 0, "patch": 0}
        tag_dict["major"] = int(tag[0]) if len(tag) >= 1 else 0
        tag_dict["minor"] = int(tag[1]) if len(tag) >= 2 else 0
        tag_dict["patch"] = int(tag[2]) if len(tag) >= 3 else 0
        return f"{tag_dict['major']:03}.{tag_dict['minor']:03}.{tag_dict['patch']:03}"
    else:
        return "000.000.000"


def get_max_version(tags):
    tagv = []
    for tag in tags:
        if tag.startswith("v"):
            tagv.append(tag)
    tagv.sort(reverse=True, key=custom_sort_key)
    return tagv[0]


def get_max_version_add_1(tag):
    tag = tag[1:].split(".")
    tag_dict = {"major": 0, "minor": 0, "patch": 0}
    tag_dict["major"] = int(tag[0]) if len(tag) >= 1 else 0
    tag_dict["minor"] = int(tag[1]) if len(tag) >= 2 else 0
    tag_dict["patch"] = int(tag[2]) if len(tag) >= 3 else 0
    tag_dict["patch"] += 1
    return f"v{tag_dict['major']}.{tag_dict['minor']}.{tag_dict['patch']}"


# cmd 打开
# git log --oneline --decorate > "D:\_code\py_code\test\a2023\b0821wxdb\test\log.txt"
# 获取当前文件所在目录
current_path = os.path.dirname(os.path.abspath(__file__))
PyWxDump_path = os.path.dirname(current_path)
log_path = os.path.join(current_path, "log.txt")
CHANGE_LOG_PATH = os.path.join(PyWxDump_path, "doc", "CHANGELOG.md")

# 调用cmd执行命令,先cd到目录  D:\_code\py_code\test\a2023\b0821wxdb\PyWxDump
os.chdir(PyWxDump_path)
os.system(f'git log --oneline --decorate > "{log_path}"')
time.sleep(0.5)

with open(log_path, "r", encoding="utf-8") as f:
    log = f.read()

# 正则匹配^(\w+){6} 并替换为空 --替换开头的commit id
log = re.sub(r"^(\w+){6} ", "", log, flags=re.MULTILINE)

log = log.replace("(HEAD -> master)", "")
log = log.replace("(HEAD -> master, origin/master, origin/HEAD)", "")
log = log.replace("(origin/master, origin/HEAD)", "")
log = log.replace("HEAD -> master, ", "").replace(", origin/master, origin/HEAD", "")

# 按照tag分割
log = log.split("(tag: ")
HEAD = log[0]
log = [i.split(")") for i in log[1:] if i]
log = {i[0]: ")".join(i[1:])[1:] for i in log}

# 将新更新的内容添加到HEAD，或者为提交到git的内容添加到HEAD
log["HEAD"] = HEAD

# 将HEAD的内容添加到最新的tag,设最新的tag为当前最大的tag+0.0.1
tags = list(log.keys())
max_version = get_max_version(tags)
max_version_add_1 = get_max_version_add_1(max_version)
log[max_version_add_1 + ".(待发布)"] = log.pop("HEAD")

# 将tag排序
tags = list(log.keys())
tags.sort(reverse=True, key=custom_sort_key)

# 生成CHANGELOG.md
CHANGE_LOG = ""

for tag in tags:
    content1 = log[tag].split("\n")
    content1 = [i.strip() for i in content1 if i.strip()]
    content1 = list(set(content1))
    content1.sort()
    content1.sort(key=lambda x: len(x))

    log[tag] = "\n".join(content1)

    CHANGE_LOG += f"## {tag}\n\n- " + "\n- ".join(content1) + "\n\n"

# 写入CHANGELOG.md
with open(CHANGE_LOG_PATH, "w", encoding="utf-8") as f:
    f.write(CHANGE_LOG[:-2])

# 删除log.txt
os.remove(log_path)

# 调用系统命令 执行git的提交
os.system(f'git add "{CHANGE_LOG_PATH}"')
os.system(f'git commit -m "UPDATE CHANGELOG.md"')
os.system(f'git push origin master')

print("CHANGELOG.md更新成功！")
