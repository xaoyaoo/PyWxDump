# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         utils.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
import hashlib
import os
import re
import time
import wave

import requests
from io import BytesIO
import pysilk
import lxml.etree as ET  # 这个模块更健壮些，微信XML格式有时有非标格式，会导致xml.etree.ElementTree处理失败
from collections import defaultdict


def type_converter(type_id_or_name: [str, tuple]):
    """
    消息类型ID与名称转换
    名称(str)=>ID(tuple)
    ID(tuple)=>名称(str)
    :param type_id_or_name: 消息类型ID或名称
    :return: 消息类型ID或名称
    """
    type_name_dict = defaultdict(lambda: "未知", {
        (1, 0): "文本",
        (3, 0): "图片",
        (34, 0): "语音",
        (37, 0): "添加好友",
        (42, 0): "推荐公众号",
        (43, 0): "视频",
        (47, 0): "动画表情",
        (48, 0): "位置",

        (49, 0): "文件",
        (49, 1): "粘贴的文本",
        (49, 3): "(分享)音乐",
        (49, 4): "(分享)卡片式链接",
        (49, 5): "(分享)卡片式链接",
        (49, 6): "文件",
        (49, 7): "游戏相关",
        (49, 8): "用户上传的GIF表情",
        (49, 15): "未知-49,15",
        (49, 17): "位置共享",
        (49, 19): "合并转发的聊天记录",
        (49, 24): "(分享)笔记",
        (49, 33): "(分享)小程序",
        (49, 36): "(分享)小程序",
        (49, 40): "(分享)收藏夹",
        (49, 44): "(分享)小说(猜)",
        (49, 50): "(分享)视频号名片",
        (49, 51): "(分享)视频号视频",
        (49, 53): "接龙",
        (49, 57): "引用回复",
        (49, 63): "视频号直播或直播回放",
        (49, 74): "文件(猜)",
        (49, 87): "群公告",
        (49, 88): "视频号直播或直播回放等",
        (49, 2000): "转账",
        (49, 2003): "赠送红包封面",

        (50, 0): "语音通话",
        (65, 0): "企业微信打招呼(猜)",
        (66, 0): "企业微信添加好友(猜)",

        (10000, 0): "系统通知",
        (10000, 1): "消息撤回1",
        (10000, 4): "拍一拍",
        (10000, 5): "消息撤回5",
        (10000, 6): "消息撤回6",
        (10000, 33): "消息撤回33",
        (10000, 36): "消息撤回36",
        (10000, 57): "消息撤回57",
        (10000, 8000): "邀请加群",
        (11000, 0): "未知-11000,0"
    })

    if isinstance(type_id_or_name, tuple):
        return type_name_dict[type_id_or_name]
    elif isinstance(type_id_or_name, str):
        return next((k for k, v in type_name_dict.items() if v == type_id_or_name), (0, 0))
    else:
        raise ValueError("Invalid input type")


def typeid2name(type_id: tuple):
    """
    获取消息类型名称
    :param type_id: 消息类型ID 元组 eg: (1, 0)
    :return:
    """
    return type_converter(type_id)


def name2typeid(type_name: str):
    """
    获取消息类型ID
    :param type_name: 消息类型名称
    :return:
    """
    return type_converter(type_name)


def get_md5(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def timestamp2str(timestamp):
    """
    时间戳转换为时间字符串
    :param timestamp: 时间戳
    :return: 时间字符串
    """
    if isinstance(timestamp, str) and timestamp.isdigit():
        timestamp = int(timestamp)
    elif isinstance(timestamp, int) or isinstance(timestamp, float):
        pass
    else:
        return timestamp

    if len(str(timestamp)) == 13:
        timestamp = timestamp / 1000
    elif len(str(timestamp)) == 10:
        pass
    else:
        return timestamp

    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def dat2img(input_data):
    """
    读取图片文件dat格式
    :param input_data:  图片文件路径或者图片文件数据
    :return:  图片格式，图片md5，图片数据
    """
    # 常见图片格式的文件头
    img_head = {
        b"\xFF\xD8\xFF": ".jpg",
        b"\x89\x50\x4E\x47": ".png",
        b"\x47\x49\x46\x38": ".gif",
        b"\x42\x4D": ".BMP",
        b"\x49\x49": ".TIFF",
        b"\x4D\x4D": ".TIFF",
        b"\x00\x00\x01\x00": ".ICO",
        b"\x52\x49\x46\x46": ".WebP",
        b"\x00\x00\x00\x18\x66\x74\x79\x70\x68\x65\x69\x63": ".HEIC",
    }

    if isinstance(input_data, str):
        with open(input_data, "rb") as f:
            input_bytes = f.read()
    else:
        input_bytes = input_data

    try:
        import numpy as np
        input_bytes = np.frombuffer(input_bytes, dtype=np.uint8)
        for hcode in img_head:  # 遍历文件头
            t = input_bytes[0] ^ hcode[0]  # 异或解密
            if np.all(t == np.bitwise_xor(np.frombuffer(input_bytes[:len(hcode)], dtype=np.uint8),
                                          np.frombuffer(hcode, dtype=np.uint8))):  # 使用NumPy进行向量化的异或解密操作，并进行类型转换
                fomt = img_head[hcode]  # 获取文件格式

                out_bytes = np.bitwise_xor(input_bytes, t)  # 使用NumPy进行向量化的异或解密操作
                md5 = get_md5(out_bytes)
                return fomt, md5, out_bytes
        return False
    except ImportError:
        pass

    for hcode in img_head:
        t = input_bytes[0] ^ hcode[0]
        for i in range(1, len(hcode)):
            if t == input_bytes[i] ^ hcode[i]:
                fomt = img_head[hcode]
                out_bytes = bytearray()
                for nowByte in input_bytes:  # 读取文件
                    newByte = nowByte ^ t  # 异或解密
                    out_bytes.append(newByte)
                md5 = get_md5(out_bytes)
                return fomt, md5, out_bytes
    return False


def xml2dict(xml_string):
    """
    解析 XML 字符串
    :param xml_string: 要解析的 XML 字符串
    :return: 解析结果，以字典形式返回
    """

    def parse_xml(element):
        """
        递归解析 XML 元素
        :param element: 要解析的 XML 元素
        :return: 解析结果，以字典形式返回
        """
        result = {}
        # 解析当前元素的属性
        if element is None or element.attrib is None:  # 有时可能会遇到没有属性，要处理下
            return result
        for key, value in element.attrib.items():
            result[key] = value
        # 解析当前元素的子元素
        for child in element:
            child_result = parse_xml(child)
            # 如果子元素的标签已经在结果中存在，则将其转换为列表
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_result)
            else:
                result[child.tag] = child_result
        # 如果当前元素没有子元素，则将其文本内容作为值保存
        if not result and element.text:
            result = element.text
        return result

    if xml_string is None or not isinstance(xml_string, str):
        return None
    try:
        parser = ET.XMLParser(recover=True)  # 有时微信的聊天记录里面，会冒出来xml格式不对的情况，这里把parser设置成忽略错误
        root = ET.fromstring(xml_string, parser)
    except Exception as e:
        return xml_string
    return parse_xml(root)


def download_file(url, save_path=None):
    """
    下载文件
    :param url: 文件下载地址
    :param save_path: 保存路径
    :return: 保存路径
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi K40 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36"

    }
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return None
    data = r.content
    if save_path and isinstance(save_path, str):
        # 创建文件夹
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        with open(save_path, "wb") as f:
            f.write(data)
    return data


def bytes2str(d):
    """
    遍历字典并将bytes转换为字符串
    :param d:
    :return:
    """
    for k, v in d.items():
        if isinstance(v, dict):
            bytes2str(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    bytes2str(item)
                elif isinstance(item, bytes):
                    item = item.decode('utf-8')  # 将bytes转换为字符串
        elif isinstance(v, bytes):
            d[k] = v.decode('utf-8')


def read_dict_all_values(data):
    """
    读取字典中所有的值（单层）
    :param dict_data: 字典
    :return: 所有值的list
    """
    result = []
    if isinstance(data, list):
        for item in data:
            result.extend(read_dict_all_values(item))
    elif isinstance(data, dict):
        for key, value in data.items():
            result.extend(read_dict_all_values(value))
    else:
        if isinstance(data, bytes):
            tmp = data.decode("utf-8")
        else:
            tmp = str(data) if isinstance(data, int) else data
        result.append(tmp)

    for i in range(len(result)):
        if isinstance(result[i], bytes):
            result[i] = result[i].decode("utf-8")
    return result


def match_BytesExtra(BytesExtra, pattern=r"FileStorage(.*?)'"):
    """
    匹配 BytesExtra
    :param BytesExtra: BytesExtra
    :param pattern: 匹配模式
    :return:
    """
    if not BytesExtra:
        return False
    BytesExtra = read_dict_all_values(BytesExtra)
    BytesExtra = "'" + "'".join(BytesExtra) + "'"
    # print(BytesExtra)

    match = re.search(pattern, BytesExtra)
    if match:
        video_path = match.group(0).replace("'", "")
        return video_path
    else:
        return ""


def silk2audio(buf_data, is_play=False, is_wave=False, save_path=None, rate=24000):
    silk_file = BytesIO(buf_data)  # 读取silk文件
    pcm_file = BytesIO()  # 创建pcm文件

    pysilk.decode(silk_file, pcm_file, rate)  # 解码silk文件->pcm文件
    pcm_data = pcm_file.getvalue()  # 获取pcm文件数据

    silk_file.close()  # 关闭silk文件
    pcm_file.close()  # 关闭pcm文件
    if is_play:  # 播放音频
        def play_audio(pcm_data, rate):
            try:
                import pyaudio
            except ImportError:
                raise ImportError("请先安装pyaudio库[ pip install pyaudio ]")

            p = pyaudio.PyAudio()  # 实例化pyaudio
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, output=True)  # 创建音频流对象
            stream.write(pcm_data)  # 写入音频流
            stream.stop_stream()  # 停止音频流
            stream.close()  # 关闭音频流
            p.terminate()  # 关闭pyaudio

        play_audio(pcm_data, rate)

    print(is_play, is_wave, save_path)

    if is_wave:  # 转换为wav文件
        wave_file = BytesIO()  # 创建wav文件
        with wave.open(wave_file, 'wb') as wf:
            wf.setparams((1, 2, rate, 0, 'NONE', 'NONE'))  # 设置wav文件参数
            wf.writeframes(pcm_data)  # 写入wav文件
        rdata = wave_file.getvalue()  # 获取wav文件数据
        wave_file.close()  # 关闭wav文件
        if save_path and isinstance(save_path, str):
            with open(save_path, "wb") as f:
                f.write(rdata)
            print('saved wav file')
        return rdata

    return pcm_data
