# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         analyser.py
# Description:  
# Author:       xaoyaoo
# Date:         2023/12/01
# -------------------------------------------------------------------------------
import sqlite3
import time
from collections import Counter
import pandas as pd

from pywxdump.dbpreprocess.utils import xml2dict
from pywxdump.dbpreprocess import parsingMSG

def date_chat_count(chat_data, interval="W"):
    """
    获取每个时间段的聊天数量
    :param chat_data: 聊天数据 json {"CreateTime":时间,"Type":消息类型,"SubType":消息子类型,"StrContent":消息内容,"StrTalker":聊天对象,"IsSender":是否发送者}
    :param interval: 时间间隔 可选值：day、month、year、week
    """
    chat_data = pd.DataFrame(chat_data)
    chat_data["CreateTime"] = pd.to_datetime(chat_data["CreateTime"])
    chat_data["AdjustedTime"] = pd.to_datetime(chat_data["CreateTime"]) - pd.Timedelta(hours=4)
    chat_data["AdjustedTime"] = chat_data["AdjustedTime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    chat_data["CreateTime"] = chat_data["CreateTime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    interval_dict = {"day": "%Y-%m-%d", "month": "%Y-%m", "year": "%Y", "week": "%Y-%W",
                     "d": "%Y-%m-%d", "m": "%Y-%m", "y": "%Y", "W": "%Y-%W"
                     }
    if interval not in interval_dict:
        raise ValueError("interval参数错误，可选值为day、month、year、week")
    chat_data["interval"] = chat_data["AdjustedTime"].dt.strftime(interval_dict[interval])

    # 根据chat_data["interval"]最大值和最小值，生成一个时间间隔列表
    interval_list = pd.date_range(chat_data["AdjustedTime"].min(), chat_data["AdjustedTime"].max(), freq=interval)
    interval_list = interval_list.append(pd.Index([interval_list[-1] + pd.Timedelta(days=1)]))  # 最后一天加一天

    # 构建数据集
    # interval type_name1 type_name2 type_name3
    # 2021-01 文本数量 其他类型数量 其他类型数量
    # 2021-02 文本数量 其他类型数量 其他类型数量
    type_data = pd.DataFrame(columns=["interval"] + list(chat_data["type_name"].unique()))
    type_data["interval"] = interval_list.strftime(interval_dict[interval])
    type_data = type_data.set_index("interval")
    for type_name in chat_data["type_name"].unique():
        type_data[type_name] = chat_data[chat_data["type_name"] == type_name].groupby("interval").size()
    type_data["全部类型"] = type_data.sum(axis=1)
    type_data["发送"] = chat_data[chat_data["IsSender"] == 1].groupby("interval").size()
    type_data["接收"] = chat_data[chat_data["IsSender"] == 0].groupby("interval").size()

    return type_data



def read_msgs(MSG_path, selected_talker=None, start_time=time.time() * 3600 * 24 * 365, end_time=time.time()):
    """
    读取消息内容-MSG.db 包含IsSender，StrContent，StrTalker，ype，SubType，CreateTime，MsgSvrID
    :param MSG_path: MSG.db 路径
    :param selected_talker: 选中的聊天对象
    :param start_time: 开始时间 时间戳10位
    :param end_time: 结束时间 时间戳10位
    :return:
    """
    type_name_dict = {
        1: {0: "文本"},
        3: {0: "图片"},
        34: {0: "语音"},
        43: {0: "视频"},
        47: {0: "动画表情"},
        49: {0: "文本", 1: "类文本消息", 5: "卡片式链接", 6: "文件", 8: "上传的GIF表情",
             19: "合并转发聊天记录", 33: "分享的小程序", 36: "分享的小程序", 57: "带有引用的文本",
             63: "视频号直播或回放等",
             87: "群公告", 88: "视频号直播或回放等", 2000: "转账消息", 2003: "红包封面"},
        50: {0: "语音通话"},
        10000: {0: "系统通知", 4: "拍一拍", 8000: "系统通知"}
    }

    # 连接 MSG_ALL.db 数据库，并执行查询
    db1 = sqlite3.connect(MSG_path)
    cursor1 = db1.cursor()

    if isinstance(start_time, str):
        start_time = time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))
    if isinstance(end_time, str):
        end_time = time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S"))

    if selected_talker is None or selected_talker == "":  # 如果 selected_talker 为 None，则查询全部对话
        cursor1.execute(
            "SELECT MsgSvrID,IsSender, StrContent, StrTalker, Type, SubType,CreateTime FROM MSG WHERE CreateTime>=? AND CreateTime<=? ORDER BY CreateTime ASC",
            (start_time, end_time))
    else:
        cursor1.execute(
            "SELECT MsgSvrID,IsSender, StrContent, StrTalker, Type, SubType,CreateTime FROM MSG WHERE StrTalker=? AND CreateTime>=? AND CreateTime<=? ORDER BY CreateTime ASC",
            (selected_talker, start_time, end_time))
    result1 = cursor1.fetchall()
    cursor1.close()
    db1.close()

    def get_emoji_cdnurl(row):
        if row["type_name"] == "动画表情":
            parsed_content = xml2dict(row["StrContent"])
            if isinstance(parsed_content, dict) and "emoji" in parsed_content:
                return parsed_content["emoji"].get("cdnurl", "")
        return row["content"]

    init_data = pd.DataFrame(result1, columns=["MsgSvrID", "IsSender", "StrContent", "StrTalker", "Type", "SubType",
                                               "CreateTime"])
    init_data["CreateTime"] = pd.to_datetime(init_data["CreateTime"], unit="s")
    init_data["AdjustedTime"] = init_data["CreateTime"] - pd.Timedelta(hours=4)
    init_data["AdjustedTime"] = init_data["AdjustedTime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    init_data["CreateTime"] = init_data["CreateTime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    init_data["type_name"] = init_data.apply(lambda x: type_name_dict.get(x["Type"], {}).get(x["SubType"], "未知"),
                                             axis=1)
    init_data["content"] = init_data.apply(lambda x: x["StrContent"] if x["type_name"] == "文本" else "", axis=1)
    init_data["content"] = init_data.apply(get_emoji_cdnurl, axis=1)

    init_data["content_len"] = init_data.apply(lambda x: len(x["content"]) if x["type_name"] == "文本" else 0, axis=1)

    chat_data = init_data[
        ["MsgSvrID", "IsSender", "StrTalker", "type_name", "content", "content_len", "CreateTime", "AdjustedTime"]]

    return True, chat_data


# 绘制直方图
def draw_hist_all_count(chat_data, out_path="", is_show=False):
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        print("error", e)
        raise ImportError("请安装matplotlib库")
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    type_count = Counter(chat_data["type_name"])

    # 对type_count按值进行排序，并返回排序后的结果
    sorted_type_count = dict(sorted(type_count.items(), key=lambda item: item[1], reverse=True))

    plt.figure(figsize=(12, 8))
    plt.bar(range(len(sorted_type_count)), list(sorted_type_count.values()), tick_label=list(sorted_type_count.keys()))
    plt.title("消息类型分布图")
    plt.xlabel("消息类型")
    plt.ylabel("数量")

    # 设置x轴标签的旋转角度为45度
    plt.xticks(rotation=-45)

    # 在每个柱上添加数字标签
    for i, v in enumerate(list(sorted_type_count.values())):
        plt.text(i, v, str(v), ha='center', va='bottom')

    if out_path != "":
        plt.savefig(out_path)
    if is_show:
        plt.show()
    plt.close()


# 按照interval绘制折线图
def draw_line_type_name(chat_data, interval="W", type_name_list=None, out_path="", is_show=False):
    """
    绘制折线图，横轴为时间，纵轴为消息数量，不同类型的消息用不同的颜色表示
    :param chat_data:
    :param interval:
    :param type_name_list: 消息类型列表，按照列表中的顺序绘制折线图 可选：全部类型、发送、接收、总字数、发送字数、接收字数、其他类型
    :param out_path:
    :param is_show:
    :return:
    """
    if type_name_list is None:
        type_name_list = ["全部类型", "发送", "接收"] + ["总字数", "发送字数", "接收字数"]
        # type_name_list = ["总字数", "发送字数", "接收字数"]

    try:
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError as e:
        print("error", e)
        raise ImportError("请安装matplotlib库")
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    chat_data["CreateTime"] = pd.to_datetime(chat_data["CreateTime"])
    chat_data["AdjustedTime"] = pd.to_datetime(chat_data["AdjustedTime"])

    # interval = interval.lower()
    interval_dict = {"day": "%Y-%m-%d", "month": "%Y-%m", "year": "%Y", "week": "%Y-%W",
                     "d": "%Y-%m-%d", "m": "%Y-%m", "y": "%Y", "W": "%Y-%W"
                     }
    if interval not in interval_dict:
        raise ValueError("interval参数错误，可选值为day、month、year、week")
    chat_data["interval"] = chat_data["AdjustedTime"].dt.strftime(interval_dict[interval])

    # 根据chat_data["interval"]最大值和最小值，生成一个时间间隔列表
    interval_list = pd.date_range(chat_data["AdjustedTime"].min(), chat_data["AdjustedTime"].max(), freq=interval)
    interval_list = interval_list.append(pd.Index([interval_list[-1] + pd.Timedelta(days=1)]))  # 最后一天加一天

    # 构建数据集
    # interval type_name1 type_name2 type_name3
    # 2021-01 文本数量 其他类型数量 其他类型数量
    # 2021-02 文本数量 其他类型数量 其他类型数量
    type_data = pd.DataFrame(columns=["interval"] + list(chat_data["type_name"].unique()))
    type_data["interval"] = interval_list.strftime(interval_dict[interval])
    type_data = type_data.set_index("interval")
    for type_name in chat_data["type_name"].unique():
        type_data[type_name] = chat_data[chat_data["type_name"] == type_name].groupby("interval").size()
    type_data["全部类型"] = type_data.sum(axis=1)
    type_data["发送"] = chat_data[chat_data["IsSender"] == 1].groupby("interval").size()
    type_data["接收"] = chat_data[chat_data["IsSender"] == 0].groupby("interval").size()

    type_data["总字数"] = chat_data.groupby("interval")["content_len"].sum()
    type_data["发送字数"] = chat_data[chat_data["IsSender"] == 1].groupby("interval")["content_len"].sum()
    type_data["接收字数"] = chat_data[chat_data["IsSender"] == 0].groupby("interval")["content_len"].sum()

    type_data = type_data.fillna(0)
    # 调整typename顺序，使其按照总数量排序，只要最大的5个
    type_data = type_data.reindex(type_data.sum().sort_values(ascending=False).index, axis=1)
    if type_name_list is not None:
        type_data = type_data[type_name_list]
    else:
        type_data = type_data.iloc[:, :5]

    # if interval == "W" or interval == "week":  # 改为当前周的周一的日期
    #     #

    plt.figure(figsize=(12, 8))

    # 绘制折线图
    for type_name in type_data.columns:
        plt.plot(type_data.index, type_data[type_name], label=type_name)

    # 设置x轴标签的旋转角度为45度
    plt.xticks(rotation=-45)
    # 设置标题、坐标轴标签、图例等信息
    plt.title("消息类型分布图")
    plt.xlabel("时间")
    plt.ylabel("数量")

    plt.legend(loc="upper right")  # 设置图例位置

    # 显示图形
    if out_path != "":
        plt.savefig(out_path)
    if is_show:
        plt.tight_layout()
        plt.show()
    plt.close()



def wordcloud_generator(chat_data, interval="m", stopwords=None, out_path="", is_show=False, bg_img=None,
                        font="C:\Windows\Fonts\simhei.ttf"):
    """
    词云
    :param is_show: 是否显示
    :param img_path: 背景图片路径
    :param text: 文本
    :param font: 字体路径
    :return:
    """
    try:
        from wordcloud import WordCloud, ImageColorGenerator
        import wordcloud
        import jieba
        import numpy as np
        import matplotlib.pyplot as plt
        from matplotlib.font_manager import fontManager
        import pandas as pd
        import codecs
        import re
        from imageio import imread
    except ImportError as e:
        print("error", e)
        raise ImportError("请安装wordcloud,jieba,numpy,matplotlib,pillow库")

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    chat_data["CreateTime"] = pd.to_datetime(chat_data["CreateTime"])
    chat_data["AdjustedTime"] = pd.to_datetime(chat_data["AdjustedTime"])

    # interval = interval.lower()
    interval_dict = {"day": "%Y-%m-%d", "month": "%Y-%m", "year": "%Y", "week": "%Y-%W",
                     "d": "%Y-%m-%d", "m": "%Y-%m", "y": "%Y", "W": "%Y-%W"
                     }
    if interval not in interval_dict:
        raise ValueError("interval参数错误，可选值为day、month、year、week")
    chat_data["interval"] = chat_data["AdjustedTime"].dt.strftime(interval_dict[interval])

    # 根据chat_data["interval"]最大值和最小值，生成一个时间间隔列表
    interval_list = pd.date_range(chat_data["AdjustedTime"].min(), chat_data["AdjustedTime"].max(), freq=interval)
    interval_list = interval_list.append(pd.Index([interval_list[-1] + pd.Timedelta(days=1)]))  # 最后一天加一天

    # 构建数据集
    # interval text_all text_sender text_receiver
    # 2021-01 文本\n合并 聊天记录\n文本\n合并 聊天记录\n文本\n合并 聊天记录\n
    def merage_text(x):
        pattern = re.compile("(\[.+?\])")  # 匹配表情
        rt = "\n".join(x)
        rt = pattern.sub('', rt).replace("\n", " ")
        return rt

    chat_data["content"] = chat_data.apply(lambda x: x["content"] if x["type_name"] == "文本" else "", axis=1)

    text_data = pd.DataFrame(columns=["interval", "text_all", "text_sender", "text_receiver"])
    text_data["interval"] = interval_list.strftime(interval_dict[interval])
    text_data = text_data.set_index("interval")
    # 使用“\n”合并
    text_data["text_all"] = chat_data.groupby("interval")["content"].apply(merage_text)
    text_data["text_sender"] = chat_data[chat_data["IsSender"] == 1].groupby("interval")["content"].apply(merage_text)
    text_data["text_receiver"] = chat_data[chat_data["IsSender"] == 0].groupby("interval")["content"].apply(merage_text)

    def gen_img(texts,out_path,is_show,bg_img,title=""):
        words = jieba.lcut(texts)
        res = [word for word in words if word not in stopwords and word.replace(" ", "") != "" and len(word) > 1]
        count_dict = dict(Counter(res))

        if bg_img:
            bgimg = imread(open(bg_img, 'rb'))
            # 获得词云对象，设定词云背景颜色及其图片和字体
            wc = WordCloud(background_color='white', mask=bgimg, font_path='simhei.ttf', mode='RGBA', include_numbers=False,
                           random_state=0)
        else:
            # 如果你的背景色是透明的，请用这两条语句替换上面两条
            bgimg = None
            wc = WordCloud(background_color='white', mode='RGBA', font_path='simhei.ttf', include_numbers=False,
                           random_state=0,width=500, height=500)  # 如果不指定中文字体路径，词云会乱码
        wc = wc.fit_words(count_dict)

        fig = plt.figure(figsize=(8, 8))
        fig.suptitle(title, fontsize=26)
        ax = fig.subplots()

        ax.imshow(wc)
        ax.axis('off')

        if out_path != "":
            plt.savefig(out_path)
        if is_show:
            plt.show()
        plt.close()

    for i in text_data.index:
        out_path = f"out/img_{i}.png"
        gen_img(text_data["text_all"][i], out_path=out_path, is_show=False, bg_img=bg_img, title=f"全部({i})")
        # gen_img(text_data["text_sender"][i], out_path="", is_show=is_show, bg_img=bg_img, title=f"发送_{i}")
        # gen_img(text_data["text_receiver"][i], out_path="", is_show=is_show, bg_img=bg_img, title=f"接收_{i}")
        # time.sleep(1)

# 情感分析
def sentiment_analysis(chat_data, stopwords="", out_path="", is_show=False, bg_img=None):
    try:
        from snownlp import SnowNLP
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns

    except ImportError as e:
        print("error", e)
        raise ImportError("请安装snownlp,pandas,matplotlib,seaborn库")

    sns.set_style('white', {'font.sans-serif': ['simhei', 'FangSong']})

    chats = []
    for row in chat_data:
        if row["type_name"] != "文本" or row["content"] == "":
            continue
        chats.append(row)

    scores = []
    for row in chats:
        s = SnowNLP(row["content"])
        scores.append(s.sentiments)

    def draw(data):
        df = pd.DataFrame({'Sentiment Score': data})
        plt.figure(figsize=(8, 6))
        sns.histplot(data=df, x='Sentiment Score', kde=True)
        plt.title("Sentiment Analysis")
        plt.xlabel("Sentiment Score")
        plt.ylabel("Frequency")

        if out_path != "":
            plt.savefig(out_path)
        if is_show:
            plt.show()
        plt.close()

    draw(scores)


if __name__ == '__main__':
    MSG_PATH = r""
    selected_talker = "wxid_"
    start_time = time.time() - 3600 * 24 * 50000
    end_time = time.time()
    code, chat_data = read_msgs(MSG_PATH, selected_talker, start_time, end_time)
    # print(chat_data)
    # code, data, classify_count, all_type_count = merge_chat_data(chat_data, interval="month")
    # draw_hist_all_count(chat_data, is_show=True)  # 绘制直方图 消息类型分布图
    # draw_line_type_name(chat_data, is_show=True)  # 绘制折线图 消息类型分布图

    # bg_img = 'img.png'
    stopwords = ['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到',
                 '说', '要',
                 '去', '你', '会', '着', '没有', '看', '好', '自己', '这']
    wordcloud_generator(chat_data, stopwords=stopwords, out_path="", is_show=True)
    # sentiment_analysis(chat_data)
