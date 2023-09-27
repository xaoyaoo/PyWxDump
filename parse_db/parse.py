# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parse.py
# Description:  解析数据库内容
# Author:       xaoyaoo
# Date:         2023/09/27
# -------------------------------------------------------------------------------
import sqlite3
import pysilk
from io import BytesIO
import wave
import pyaudio
import requests
import hashlib

from PIL import Image
import xml.etree.ElementTree as ET


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
        root = ET.fromstring(xml_string)
    except Exception as e:
        return xml_string
    return parse_xml(root)


def read_img_dat(input_data):
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
    fomt = "un"  # 文件格式

    if isinstance(input_data, str):
        with open(input_data, "rb") as f:
            input_bytes = f.read()

    t = 0
    for hcode in img_head:
        t = input_bytes[0] ^ hcode[0]
        for i in range(1, len(hcode)):
            if t == input_bytes[i] ^ hcode[i]:
                fomt = img_head[hcode]
            else:
                break
        else:
            break
    else:
        return False

    if fomt == "un":
        print("未知文件格式")
        return False

    out_bytes = bytearray()
    for nowByte in input_bytes:  # 读取文件
        newByte = nowByte ^ t  # 异或解密
        out_bytes.append(newByte)

    md5 = get_md5(out_bytes)
    return fomt, md5, out_bytes

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
    i = 0
    uncompressed_data = []

    while i < len(data):
        # 读取第一个字节
        byte1 = data[i]
        # 从高四位得到无匹配的明文长度Lh
        Lh = byte1 >> 4
        Li = byte1 & 0x0F  # 从低四位得到匹配的数据长度Li
        if Lh == 0x0f:
            # 继续读取下一个字节L1
            i = i + 1
            L1 = data[i]
            Lh = L1 + 0x0f

            while data[i] == 0xFF:
                # 继续读取下一个字节，并累加
                i = i + 1
                Lh += data[i]
        i += 1
        uncompressed_data.extend(data[i:i + Lh])
        i = i + Lh

        # 读取匹配的偏移量Offset
        bias = data[i:i + 2]
        offset = int.from_bytes(bias, byteorder='little')
        i = i + 2

        # 读取匹配的数据长度Li
        if Li != 0x0F:
            # 实际的匹配压缩长度即为Li = Li + 4
            Li += 4
        else:
            # 从偏移量后面的可选匹配长度区域读取一个字节M1
            M1 = data[i]
            Li += M1
            while M1 == 0xFF:
                # 继续读取下一个字节M2
                i += 1
                M1 = data[i]
                Li += M1
            Li += 4
        # 复制匹配的数据到解压缩数据缓冲区
        uncompressed_data.extend(uncompressed_data[-offset:-offset + Li])
        # break

    # 转换为字符串
    uncompressed_data = bytes(uncompressed_data)  # .decode('utf-8')
    return uncompressed_data


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
    sql = "select Buf from Media where Reserved0='{}'".format(MsgSvrID)
    DBdata = cursor.execute(sql).fetchall()

    if len(DBdata) == 0:
        return False

    data = DBdata[0][0]  # [1:] + b'\xFF\xFF'

    pcm_data = read_audio_buf(data, is_play, is_wave, rate)

    return pcm_data


if __name__ == '__main__':
    pass
