# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parse.py
# Description:  解析数据库内容
# Author:       xaoyaoo
# Date:         2023/09/27
# -------------------------------------------------------------------------------
import os.path
import sqlite3
import pysilk
from io import BytesIO
import wave
import pyaudio
import requests
import hashlib
import lz4.block
import blackboxprotobuf

from PIL import Image
# import xml.etree.ElementTree as ET
import lxml.etree as ET  # 这个模块更健壮些，微信XML格式有时有非标格式，会导致xml.etree.ElementTree处理失败


def get_md5(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def parse_xml_string(xml_string):
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


def read_img_dat(input_data):
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


def read_emoji(cdnurl, is_show=False):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi K30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36"

    }
    r1 = requests.get(cdnurl, headers=headers)
    rdata = r1.content

    if is_show:  # 显示表情
        img = Image.open(BytesIO(rdata))
        img.show()
    return rdata


def decompress_CompressContent(data):
    """
    解压缩Msg：CompressContent内容
    :param data:
    :return:
    """
    if data is None or not isinstance(data, bytes):
        return None
    try:
        dst = lz4.block.decompress(data, uncompressed_size=len(data) << 8)
        dst = dst.replace(b'\x00', b'')  # 已经解码完成后，还含有0x00的部分，要删掉，要不后面ET识别的时候会报错
        uncompressed_data = dst.decode('utf-8', errors='ignore')
        return uncompressed_data
    except Exception as e:
        return data.decode('utf-8', errors='ignore')


def read_audio_buf(buf_data, is_play=False, is_wave=False, rate=24000):
    silk_file = BytesIO(buf_data)  # 读取silk文件
    pcm_file = BytesIO()  # 创建pcm文件

    pysilk.decode(silk_file, pcm_file, rate)  # 解码silk文件->pcm文件
    pcm_data = pcm_file.getvalue()  # 获取pcm文件数据

    silk_file.close()  # 关闭silk文件
    pcm_file.close()  # 关闭pcm文件
    if is_play:  # 播放音频
        def play_audio(pcm_data, rate):
            p = pyaudio.PyAudio()  # 实例化pyaudio
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, output=True)  # 创建音频流对象
            stream.write(pcm_data)  # 写入音频流
            stream.stop_stream()  # 停止音频流
            stream.close()  # 关闭音频流
            p.terminate()  # 关闭pyaudio

        play_audio(pcm_data, rate)

    if is_wave:  # 转换为wav文件
        wave_file = BytesIO()  # 创建wav文件
        with wave.open(wave_file, 'wb') as wf:
            wf.setparams((1, 2, rate, 0, 'NONE', 'NONE'))  # 设置wav文件参数
            wf.writeframes(pcm_data)  # 写入wav文件
        rdata = wave_file.getvalue()  # 获取wav文件数据
        wave_file.close()  # 关闭wav文件
        return rdata

    return pcm_data


def read_audio(MsgSvrID, is_play=False, is_wave=False, DB_PATH: str = "", rate=24000):
    if DB_PATH == "":
        return False

    DB = sqlite3.connect(DB_PATH)
    cursor = DB.cursor()
    sql = "select Buf from Media where Reserved0={}".format(MsgSvrID)
    DBdata = cursor.execute(sql).fetchall()

    if len(DBdata) == 0:
        return False
    data = DBdata[0][0]  # [1:] + b'\xFF\xFF'
    try:
        pcm_data = read_audio_buf(data, is_play, is_wave, rate)
        return pcm_data
    except Exception as e:
        return False


def wordcloud_generator(text, out_path="", is_show=False, img_path="", font="C:\Windows\Fonts\simhei.ttf"):
    """
    词云
    :param is_show: 是否显示
    :param img_path: 背景图片路径
    :param text: 文本
    :param font: 字体路径
    :return:
    """
    try:
        from wordcloud import WordCloud
        import jieba
        import numpy as np
        import matplotlib.pyplot as plt
        from matplotlib.font_manager import fontManager
    except ImportError as e:
        print("error", e)
        raise ImportError("请安装wordcloud,jieba,numpy,matplotlib,pillow库")
    words = jieba.lcut(text)  # 精确分词
    newtxt = ' '.join(words)  # 空格拼接
    # 字体路径

    # 创建WordCloud对象
    wordcloud1 = WordCloud(width=800, height=400, background_color='white', font_path=font)
    wordcloud1.generate(newtxt)

    if out_path and out_path != "":
        wordcloud1.to_file("wordcloud.png")  # 保存图片
    if img_path and os.path.exists(img_path):  # 设置背景图片
        img_color = np.array(Image.open(img_path))  # 读取背景图片
        img_color = img_color.reshape((img_color.shape[0] * img_color.shape[1], 3))
        wordcloud1.recolor(color_func=img_color)  # 设置背景图片颜色
    if is_show:
        # 显示词云
        wordcloud_img = wordcloud1.to_image()
        wordcloud_img.show()


def convert_bytes_to_str(d):
    """
    遍历字典并将bytes转换为字符串
    :param d:
    :return:
    """
    for k, v in d.items():
        if isinstance(v, dict):
            convert_bytes_to_str(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    convert_bytes_to_str(item)
                elif isinstance(item, bytes):
                    item = item.decode('utf-8')  # 将bytes转换为字符串
        elif isinstance(v, bytes):
            d[k] = v.decode('utf-8')


def read_BytesExtra(BytesExtra):
    if BytesExtra is None or not isinstance(BytesExtra, bytes):
        return None
    try:
        deserialize_data, message_type = blackboxprotobuf.decode_message(BytesExtra)
        return deserialize_data
    except Exception as e:
        return None


def read_ChatRoom_RoomData(RoomData):
    # 读取群聊数据,主要为 wxid，以及对应昵称
    if RoomData is None or not isinstance(RoomData, bytes):
        return None
    try:
        data = read_BytesExtra(RoomData)
        convert_bytes_to_str(data)
        return data
    except Exception as e:
        return None
