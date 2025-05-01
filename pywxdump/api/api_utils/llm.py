# LLM api相关
import enum
import json
import os
import re

import httpx
from openai import OpenAI

from pywxdump.api.remote_server import gc




class BaseLLMApi(object):
    def __init__(self,api_key,base_url=None):
        # 设置名字，以供其他函数使用 !!!不使用，
        # self.api_key_string = "API_KEY"
        # self.base_url_string = "BASE_URL"
        # self.env_api_key_string = self.__class__.__name__ + "_" + self.api_key_string
        # self.env_base_url_string = self.__class__.__name__ + "_" + self.base_url_string
        # self.setting_string = self.__class__.__name__ + "_setting"


        self.API_KEY = api_key
        self.BASE_URL = base_url

        self.module = (

        )#模型列表


        self.HTTP_CLIENT = None
        self.isReady = False
        self.message = []


        # 执行初始化方法
        self.set_default_fn()




    def set_default_fn(self):
        if not self.module:
            self.set_default_module()
        if not self.BASE_URL:
            self.set_default_base_url()
        if not self.message:
            self.set_default_message()

    def set_default_module(self):
        self.module = ()

    def set_default_base_url(self):
        self.BASE_URL = ""

    def set_default_message(self):
        self.message = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ]



    def set_module(self, module):
        self.module = module

    def set_api_key(self, api_key):
        self.API_KEY = api_key

    def set_base_url(self, base_url):
        self.BASE_URL = base_url


    def set_message(self, message):
        self.message = message





    # def ready(self):
    #     if not self.API_KEY:
    #         # 从配置中获取，这个功能必须配合网页API开启后才能使用
    #         self.API_KEY = gc.get_conf(gc.at,self.setting_string)[self.api_key_string]
    #         if not self.API_KEY:
    #             raise RuntimeError("API_KEY must be set")
    #         # 设置环境变量
    #         os.environ[self.env_api_key_string] = self.API_KEY
    #         os.environ[self.env_base_url_string] = self.BASE_URL
    #
    #     self.isReady = True
    #     return


    def ready(self):
        if not self.BASE_URL and not self.API_KEY:
            raise RuntimeError("API_KEY or BASE_URL must be set")
        self.isReady = True



    @property
    def http_client(self):
        if not self.isReady:
            self.ready()
        try:
            self.HTTP_CLIENT = OpenAI(api_key=self.API_KEY, base_url=self.BASE_URL)
            return self.HTTP_CLIENT
        except:
            raise RuntimeError("HTTP_CLIENT set not successfully,please check!")







    def send_msg(self, message=None, module=None, stream=False):
        """
        向大模型发送信息
        如果非流式返回，则直接输出内容，
        否则使用openai文档规定格式输出
        """

        if message is None:
            message = self.message

        response = self.http_client.chat.completions.create(
            model=self.module[module],
            messages=message,
            stream=stream
        )
        if not stream:
            return self.process_msg(response.choices[0].message.content)
        else:
            return self.process_msg(response.response.read().decode("utf-8"))

    def process_msg(self,x):
        return x

class DeepSeekApi(BaseLLMApi):


    def set_default_module(self):
        self.module = (
            "deepseek-chat",
            "deepseek-reasoner"
        )

    def set_default_base_url(self):
        self.BASE_URL = "https://api.deepseek.com"

    def set_default_message(self):
        self.message = [
            {"role": "system", "content": """从内容中提取出以下信息，可以根据内容多少进行列表扩展或增加，请仔细思索怎么填充内容，如果没有给到合理的名称或其他内容，就以合理的方式思考并添加。

                    - 最后的输出值使用严格的json格式

                    - 不要私自添加json块或减少json块

                    - 内容中不要使用换行符，如果内容原本有多个换行符，删掉原本多余的的换行符，只保留一个换行符再加入进去。

                    - 内容中如果有很奇怪的字符，比如''\''或''\\''影响代码编译的字符，删除原本的字符再加入进去。



                    {

                    "header": {

                    "title": "[群名称]报告",

                    "date": "[日期]",

                    "metaInfo": {

                    "totalMessages": "[数量]",

                    "activeUsers": "[数量]",

                    "timeRange": "[时间范围]"

                    }

                    },

                    "sections": {

                    "hotTopics": {

                    "items": [

                    {

                    "name": "[热点话题名称]",

                    "category": "[话题分类]",

                    "summary": "[简要总结(50-100字)]",

                    "keywords": ["[关键词1]", "[关键词2]"],

                    "mentions": "[次数]"

                    }

                    ]

                    },

                    "tutorials": {

                    "items": [

                    {

                    "type": "[TUTORIAL | NEWS | RESOURCE]",

                    "title": "[分享的教程或资源标题]",

                    "sharedBy": "[昵称]",

                    "time": "[时间]",

                    "summary": "[内容简介]",

                    "keyPoints": ["[要点1]", "[要点2]"],

                    "url": "[URL]",

                    "domain": "[域名]",

                    "category": "[分类]"

                    }

                    ]

                    },

                    "importantMessages": {

                    "items": [

                    {

                    "time": "[消息时间]",

                    "sender": "[发送者昵称]",

                    "type": "[NOTICE | EVENT | ANNOUNCEMENT | OTHER]",

                    "priority": "[高|中|低]",

                    "content": "[消息内容]",

                    "fullContent": "[完整通知内容]"

                    }

                    ]

                    },

                    "dialogues": {

                    "items": [

                    {

                    "type": "[DIALOGUE | QUOTE]",

                    "messages": [

                    {

                    "speaker": "[说话者昵称]",

                    "time": "[发言时间]",

                    "content": "[消息内容]"

                    }

                    ],

                    "highlight": "[对话中的金句或亮点]",

                    "relatedTopic": "[某某话题]"

                    }

                    ]

                    },

                    "qa": {

                    "items": [

                    {

                    "question": {

                    "asker": "[提问者昵称]",

                    "time": "[提问时间]",

                    "content": "[问题内容]",

                    "tags": ["[相关标签1]", "[相关标签2]"]

                    },

                    "answers": [

                    {

                    "responder": "[回答者昵称]",

                    "time": "[回答时间]",

                    "content": "[回答内容]",

                    "isAccepted": true

                    }

                    ]

                    }

                    ]

                    },

                    "analytics": {

                    "heatmap": [

                    {

                    "topic": "[话题名称]",

                    "percentage": "[百分比]",

                    "color": "#3da9fc",

                    "count": "[数量]"

                    }

                    ],

                    "chattyRanking": [

                    {

                    "rank": 1,

                    "name": "[群友昵称]",

                    "count": "[数量]",

                    "characteristics": ["[特点1]", "[特点2]"],

                    "commonWords": ["[常用词1]", "[常用词2]"]

                    }

                    ],

                    "nightOwl": {

                    "name": "[熬夜冠军昵称]",

                    "title": "[熬夜冠军称号]",

                    "latestTime": "[时间]",

                    "messageCount": "[数量]",

                    "lastMessage": "[最后一条深夜消息内容]"

                    }

                    },

                    "wordCloud": {

                    "words": [

                    {

                    "text": "[关键词1]",

                    "size": 38,

                    "color": "#00b4d8",

                    "rotation": -15

                    }

                    ],

                    "legend": [

                    {"color": "#00b4d8", "label": "[分类1] 相关词汇"},

                    {"color": "#4361ee", "label": "[分类2] 相关词汇"}

                    ]

                    }

                    },

                    "footer": {

                    "dataSource": "[群名称]聊天记录",

                    "generationTime": "[当前时间]",

                    "statisticalPeriod": "[日期] [时间范围]",

                    "disclaimer": "本报告内容基于群聊公开讨论，如有不当内容或侵权问题请联系管理员处理。"

                    }

                    }"""},
            {"role": "user", "content": """你好，以下是我要提取的内容: [
                {
                    "sender": "ಠ_ಠ 闲鱼一条ಠ_ಠ",
                    "content": "[强]",
                    "timestamp": "2025-04-29 07:03:10"
                },
                {
                    "sender": "JustinZ",
                    "content": "OK",
                    "timestamp": "2025-04-29 07:59:23"
                },
                {
                    "sender": "AHapi²⁰²⁵",
                    "content": "[旺柴]贿赂三星  这词",
                    "timestamp": "2025-04-29 08:01:17"
                },
                {
                    "sender": "好名字",
                    "content": "这个我弄完，ai做的小程序有bug，流程走不通，还改不了[捂脸]\n\n[引用](2025-04-28 12:02:27)苍何:用AI一句话开发了个名片制作微信小程序，前后台系统都有，还能一键发布！",
                    "timestamp": "2025-04-29 08:16:23"
                },
                {
                    "sender": "贾👦🏻",
                    "content": "可以微调 不过源码需要买的\n\n[引用](2025-04-29 08:16:23)好名字:这个我弄完，ai做的小程序有bug，流程走不通，还改不了[捂脸]",
                    "timestamp": "2025-04-29 08:54:33"
                },
                {
                    "sender": "好名字",
                    "content": "微调一次，然后再想调就需要开会员了",
                    "timestamp": "2025-04-29 09:13:32"
                },
                {
                    "sender": "贾👦🏻",
                    "content": "需求变更一个字 就需要重新购买[破涕为笑]",
                    "timestamp": "2025-04-29 09:14:09"
                },
                {
                    "sender": "AHapi²⁰²⁵",
                    "content": "表情",
                    "timestamp": "2025-04-29 09:14:22"
                },
                {
                    "sender": "苍何",
                    "content": "Qwen3深夜正式开源，小尺寸也能大力出奇迹。\n欢迎来到这个荒诞又灿烂的时代。\n\n<a href=\"http://mp.weixin.qq.com/s?__biz=MzIyMzA5NjEyMA==&mid=2647670717&idx=1&sn=edec1f6cda0c1227e72cd07abf4228ff&chksm=f19a699bb993eb9ed2850ba329f382668bc7edc8a2d7d4a94de2d29c15cf87aa05bf6b48dc6d&mpshare=1&scene=1&srcid=0429TzXAJtS5jA2QI9hLEroV&sharer_shareinfo=7fd7493f3ccf9923f55b48a05619ce1b&sharer_shareinfo_first=fc872ba73c219b858d700a9db530b5b1#rd\" target=\"_blank\">点击查看详情</a>",
                    "timestamp": "2025-04-29 09:20:23"
                },
                {
                    "sender": "沙皮狗的忧伤",
                    "content": "苍老师，没写一篇",
                    "timestamp": "2025-04-29 09:26:19"
                },
                {
                    "sender": "苍何",
                    "content": "我熬不动",
                    "timestamp": "2025-04-29 09:26:49"
                },
                {
                    "sender": "AHapi²⁰²⁵",
                    "content": "不要卷别人[旺柴]别人写了 就不卷他们了",
                    "timestamp": "2025-04-29 09:27:25"
                },
                {
                    "sender": "苍何",
                    "content": "新闻得第一时间，做不到写了也没啥用",
                    "timestamp": "2025-04-29 09:27:55"
                },
                {
                    "sender": "苍何",
                    "content": "还不如写些应用",
                    "timestamp": "2025-04-29 09:28:03"
                },
                {
                    "sender": "大风（Wind）",
                    "content": "看看哪些是5-7点发推文的，基本都是卷王了",
                    "timestamp": "2025-04-29 09:28:23"
                },
                {
                    "sender": "沉默王二",
                    "content": "身体能扛住确实离谱",
                    "timestamp": "2025-04-29 09:28:44"
                },
                {
                    "sender": "苍何",
                    "content": "是啊，太肝了",
                    "timestamp": "2025-04-29 09:29:03"
                },
                {
                    "sender": "苍何",
                    "content": "我前天熬夜测vidu，人已经废了好几天",
                    "timestamp": "2025-04-29 09:29:39"
                },
                {
                    "sender": "AHapi²⁰²⁵",
                    "content": "5-7点还好 早点睡也还行",
                    "timestamp": "2025-04-29 09:30:02"
                },
                {
                    "sender": "大风（Wind）",
                    "content": "效果咋样\n\n[引用](2025-04-29 09:29:39)苍何:\n我前天熬夜测vidu，人已经废了好几天",
                    "timestamp": "2025-04-29 09:30:14"
                },
                {
                    "sender": "大风（Wind）",
                    "content": "5点发布的\n\n[引用](2025-04-29 09:30:02)AHapi²⁰²⁵:\n5-7点还好 早点睡也还行",
                    "timestamp": "2025-04-29 09:30:21"
                },
                {
                    "sender": "大风（Wind）",
                    "content": "2小时内出文",
                    "timestamp": "2025-04-29 09:30:52"
                },
                {
                    "sender": "沉默王二",
                    "content": "意味着阿里的 coder 们也在加班和熬夜",
                    "timestamp": "2025-04-29 09:31:00"
                },
                {
                    "sender": "苍何",
                    "content": "体验完刚上线的Vidu Q1，后劲有点大（附AI视频创作教程）\nAI视频清晰度，一致性都上了一个台阶\n\n<a href=\"http://mp.weixin.qq.com/s?__biz=MzU4NTE1Mjg4MA==&mid=2247493267&idx=1&sn=0189fb501578ce8e27142fbe2f590d03&chksm=fc9a946728c367005c19cb5a335300d05d51a441f9f20424a0a72c904a47bdf003252576318a&mpshare=1&scene=1&srcid=04297l70B2zsuypDfjUh0rh5&sharer_shareinfo=181efb947f938ab90786c776bf7bbda7&sharer_shareinfo_first=181efb947f938ab90786c776bf7bbda7#rd\" target=\"_blank\">点击查看详情</a>",
                    "timestamp": "2025-04-29 09:39:42"
                },
                {
                    "sender": "苍何",
                    "content": "@大风（Wind） 你看看，效果还可以",
                    "timestamp": "2025-04-29 09:40:01"
                },
                {
                    "sender": "AHapi²⁰²⁵",
                    "content": "他们加班熬夜 赚的还是多啊[Facepalm]我们加班熬夜 就一点屁钱\n\n[引用](2025-04-29 09:31:00)沉默王二:意味着阿里的 coder 们也在加班和熬夜",
                    "timestamp": "2025-04-29 09:40:18"
                },
                {
                    "sender": "苍何",
                    "content": "阿里新出的夸克AI相机，强大到我有点陌生。\n夸克AI相机超多新奇的玩法，太抽象了。\n\n<a href=\"http://mp.weixin.qq.com/s?__biz=MzU4NTE1Mjg4MA==&mid=2247493275&idx=1&sn=93556ddd1da7fb8733a23a7c4adbb76b&chksm=fc2a2d25774cce23c75acd8850b85c585c0bcf78d14b810e157efaec5106abf563cf58e26aef&mpshare=1&scene=1&srcid=0429vDf8NbEzNLBQQyFlABmU&sharer_shareinfo=28b94477ec8201b88aa30338e82e8999&sharer_shareinfo_first=28b94477ec8201b88aa30338e82e8999#rd\" target=\"_blank\">点击查看详情</a>",
                    "timestamp": "2025-04-29 09:42:38"
                },
                {
                    "sender": "苍何",
                    "content": "我熬夜写了这一篇[旺柴]",
                    "timestamp": "2025-04-29 09:42:54"
                },
                {
                    "sender": "AHapi²⁰²⁵",
                    "content": "成功还得肝啊",
                    "timestamp": "2025-04-29 09:43:15"
                },
                {
                    "sender": "苍何",
                    "content": "2025年04月29日 AI科技早报\n\n1、阿里开源8款Qwen3模型，集成MCP，性能超DeepSeek-R1、OpenAI o1。\n\n2、Qafind Labs发布ChatDLM扩散语言模型，推理速度高达2800 tokens/s。\n\n3、腾讯开源Kuikly跨端框架，基于Kotlin支持多平台开发，已应用于QQ。\n\n4、OpenAI 推出 ChatGPT 购物功能，用户可通过 ChatGPT 便捷购物。\n\n5、字节Seed团队提出PHD-Transformer，突破预训练长度扩展瓶颈。\n\n6、百度发布文心快码3.5版本与多模态AI智能体Zulu，助力工程师提效。\n\n7、Kimi与财新传媒合作，提供专业财经内容，推动AI+传统媒体融合。\n\n8、苹果加速「N50」智能眼镜项目，融合AI技术预计2027年亮相。\n\n9、研究显示OpenAI o3在病毒学领域超越94%人类专家，生物安全引关注。\n\n10、华为测试自研AI芯片Ascend 910D，旨在替代英伟达H100芯片。\n\n11、🔥【记得收藏】早报同步更新到开源 AI 知识库：https://u55dyuejxc.feishu.cn/wiki/FkmNwxYHDigJ3akIUGHc8MSTn4d",
                    "timestamp": "2025-04-29 10:00:18"
                },
                {
                    "sender": "银色子弹-捷",
                    "content": "问一下win11电脑，你长时间没清理，运行慢，一般用什么来清理电脑？ 不要360啊，那个太流氓了，想知道各位大佬有没有优秀的软件推荐一下",
                    "timestamp": "2025-04-29 11:10:26"
                },
                {
                    "sender": "昏沉沉的",
                    "content": "ccclean",
                    "timestamp": "2025-04-29 11:11:59"
                },
                {
                    "sender": "昏沉沉的",
                    "content": "我拍了拍\"银色子弹-捷\"[炸弹]",
                    "timestamp": "2025-04-29 11:12:04"
                },
                {
                    "sender": "🤑程序儒",
                    "content": "360极速版、Wise Care 365",
                    "timestamp": "2025-04-29 11:13:07"
                },
                {
                    "sender": "AHapi²⁰²⁵",
                    "content": "仅2MB，Windows瞬间超级丝滑！\n这才是，真神器！\n\n<a href=\"https://mp.weixin.qq.com/s/es77Jc6Du03ppJD5XJeQUg\" target=\"_blank\">点击查看详情</a>",
                    "timestamp": "2025-04-29 11:13:38"
                },
                {
                    "sender": "银色子弹-捷",
                    "content": "好的，我去尝试一下",
                    "timestamp": "2025-04-29 11:21:41"
                },
                {
                    "sender": "银色子弹-捷",
                    "content": "感谢",
                    "timestamp": "2025-04-29 11:21:53"
                },
                {
                    "sender": "ಠ_ಠ 闲鱼一条ಠ_ಠ",
                    "content": "请问哪位哥还有扣子的邀请码吗？",
                    "timestamp": "2025-04-29 11:37:49"
                },
                {
                    "sender": "贾👦🏻",
                    "content": "RootUser_2105656329 邀请你体验扣子空间，快来和 Agent 一起开始你的工作吧！\nhttps://www.coze.cn/space-preview?invite_code=SCL7DAL0",
                    "timestamp": "2025-04-29 11:40:37"
                },
                {
                    "sender": "ಠ_ಠ 闲鱼一条ಠ_ಠ",
                    "content": "感谢[抱拳]",
                    "timestamp": "2025-04-29 11:42:45"
                },
                {
                    "sender": "9527",
                    "content": "RootUser_2106519373 邀请你体验扣子空间，快来和 Agent 一起开始你的工作吧！\nhttps://www.coze.cn/space-preview?invite_code=A8IT4MUE",
                    "timestamp": "2025-04-29 11:47:43"
                },
                {
                    "sender": "9527",
                    "content": "RootUser_2106519373 邀请你体验扣子空间，快来和 Agent 一起开始你的工作吧！\nhttps://www.coze.cn/space-preview?invite_code=7QUCYZKC",
                    "timestamp": "2025-04-29 11:47:53"
                },
                {
                    "sender": "AHapi²⁰²⁵",
                    "content": "Qwen3：心性\n可与之「坐而论道」\n\n<a href=\"http://mp.weixin.qq.com/s?__biz=MzkxMzc1NzM1Mw==&mid=2247484627&idx=1&sn=7c7a94d29958190891ad226b5ec5cc38&chksm=c015d84ed34eb92b1984f9dd3398a5c6aff8c2353926ddf32d9c3ba63ec6b9397c44f9acde43&mpshare=1&scene=1&srcid=0429iLCl6ZCYkHKLUVjGjJSC&sharer_shareinfo=2cbd22d2f91edbb0c1b4fbe3d89519d0&sharer_shareinfo_first=2cbd22d2f91edbb0c1b4fbe3d89519d0#rd\" target=\"_blank\">点击查看详情</a>",
                    "timestamp": "2025-04-29 15:36:25"
                },
                {
                    "sender": "苍何",
                    "content": "(分享)视频号视频",
                    "timestamp": "2025-04-29 21:08:34"
                },
                {
                    "sender": "维金",
                    "content": "挺牛的",
                    "timestamp": "2025-04-29 21:10:30"
                },
                {
                    "sender": "NowIsFuture",
                    "content": "表情",
                    "timestamp": "2025-04-29 21:15:45"
                },
                {
                    "sender": "昏沉沉的",
                    "content": "群里有没有做智能体开发的小伙伴  我现在有个问题",
                    "timestamp": "2025-04-29 21:20:53"
                },
                {
                    "sender": "昏沉沉的",
                    "content": "还有没有coze邀请码啊？",
                    "timestamp": "2025-04-29 21:27:15"
                },
                {
                    "sender": "昏沉沉的",
                    "content": "大佬们",
                    "timestamp": "2025-04-29 21:27:18"
                },
                {
                    "sender": "Angora",
                    "content": "HT2QP13K 这个你试试\n\n[引用](2025-04-29 21:27:16)昏沉沉的:还有没有coze邀请码啊？",
                    "timestamp": "2025-04-29 21:28:38"
                },
                {
                    "sender": "昏沉沉的",
                    "content": "感谢",
                    "timestamp": "2025-04-29 21:29:36"
                },
                {
                    "sender": "Angora",
                    "content": "表情",
                    "timestamp": "2025-04-29 21:30:03"
                },
                {
                    "sender": "虫虫",
                    "content": "新手学习神经网络",
                    "timestamp": "2025-04-29 23:38:02"
                },
                {
                    "sender": "虫虫",
                    "content": "RNN｜什么是循环神经网络？为什么它能“记住”过去？\nRNN（卷积神经网络）\n\n<a href=\"http://mp.weixin.qq.com/s?__biz=Mzk3NTI3NzE1OA==&mid=2247483990&idx=1&sn=ec2b8b7a0a083101d5efc7edf44a6b08&chksm=c5c9a8cc4ae1e6ed32141e22e4685bb085725c7577406e6432ea09fdc09080cab67ea7b26bc9&mpshare=1&scene=1&srcid=0429B4XDtHLFVkYtCmYDKAlu&sharer_shareinfo=fe79b1f510734762eebf9ac7f0e05049&sharer_shareinfo_first=fe79b1f510734762eebf9ac7f0e05049#rd\" target=\"_blank\">点击查看详情</a>",
                    "timestamp": "2025-04-29 23:38:02"
                },
                {
                    "sender": "苍何",
                    "content": "2025年04月30日 AI科技早报\n\n1、习近平总书记调研上海 “模速空间” ，关注人工智能发展。\n\n2、通义App及网页版新增开源模型 Qwen3，用户可体验智能对话功能。\n\n3、马斯克将发Grok 3.5早期测试版，仅限订阅用户，专攻专业领域解答。\n\n4、Meta推AI助手Meta AI APP，融合社交，支持文字语音互动及图像生成。\n\n5、ChatGPT被指对未成年生成色情内容，OpenAI确认并将紧急修复。\n\n6、宇树科技G1机器人完成13.2公里长跑，118分钟续航回应马拉松摔倒质疑。\n\n7、微软与OpenAI因算力、模型权限及 AGI 开发等问题分歧加剧，关系趋紧。\n\n8、智象未来HiDream-I1模型被谷歌收录，多项指标超GPT-4o与Flux1.1。\n\n9、联合包裹计划与 Figure AI 合作部署人形机器人，提升物流效率。\n\n10、星纪魅族与蚂蚁国际将推智能眼镜线下支付功能，预计第三季度落地。\n\n11、🔥【记得收藏】早报同步更新到开源 AI 知识库：https://u55dyuejxc.feishu.cn/wiki/FkmNwxYHDigJ3akIUGHc8MSTn4d",
                    "timestamp": "2025-04-30 10:00:20"
                },
                {
                    "sender": "苍何",
                    "content": "手搓完字节AI硬件，我做了个五一智能旅行小装置（附万字沉浸式教程）\n用AI硬件做了个智能旅行小装置\n\n<a href=\"http://mp.weixin.qq.com/s?__biz=MzU4NTE1Mjg4MA==&mid=2247493285&idx=1&sn=786bab4a79aa7268132e73868682a7a2&chksm=fc1640a0ed5d05149a71694489c36fc4f883b929f0adadc3091ed3b33868cd485821805a5852&mpshare=1&scene=1&srcid=0430ZGlkKd3PTEbnmA0gggS0&sharer_shareinfo=25ac984fb16d1db62435b2184986e7f3&sharer_shareinfo_first=fca869d864c78f40983f522434577929#rd\" target=\"_blank\">点击查看详情</a>",
                    "timestamp": "2025-04-30 11:05:21"
                },
                {
                    "sender": "枫哥 Prompter",
                    "content": "[强]牛气冲天\n\n[引用](2025-04-30 11:05:21)苍何:手搓完字节AI硬件，我做了个五一智能旅行小装置（附万字沉浸式教程）",
                    "timestamp": "2025-04-30 12:59:03"
                },
                {
                    "sender": "听说",
                    "content": "塞到玩偶里，出门你走路上都是最靓的仔\n\n[引用](2025-04-30 11:05:21)苍何:手搓完字节AI硬件，我做了个五一智能旅行小装置（附万字沉浸式教程）",
                    "timestamp": "2025-04-30 13:02:39"
                },
                {
                    "sender": "兔子先生",
                    "content": "定制女友角色\n\n[引用](2025-04-30 11:05:21)苍何:手搓完字节AI硬件，我做了个五一智能旅行小装置（附万字沉浸式教程）",
                    "timestamp": "2025-04-30 13:13:35"
                },
                {
                    "sender": "银色子弹-捷",
                    "content": "图片",
                    "timestamp": "2025-04-30 15:13:20"
                },
                {
                    "sender": "银色子弹-捷",
                    "content": "@苍何 这个设备相当于是语音话筒吗？ 真正大模型在云端高的是吗？",
                    "timestamp": "2025-04-30 15:13:57"
                },
                {
                    "sender": "银色子弹-捷",
                    "content": "那这样的话手机本身也能做为这个终端啊，未什么要这个设备呢？ 请教一下",
                    "timestamp": "2025-04-30 15:14:27"
                },
                {
                    "sender": "昏沉沉的",
                    "content": "产品\n\n[引用](2025-04-30 15:14:27):那这样的话手机本身也能做为这个终端啊，未什么要这个设备呢？ 请教一下",
                    "timestamp": "2025-04-30 15:17:57"
                },
                {
                    "sender": "昏沉沉的",
                    "content": "可以嵌入到其他东西里面",
                    "timestamp": "2025-04-30 15:18:10"
                },
                {
                    "sender": "昏沉沉的",
                    "content": "比如娃娃",
                    "timestamp": "2025-04-30 15:18:14"
                },
                {
                    "sender": "银色子弹-捷",
                    "content": "各种高端玩具倒是可以啊",
                    "timestamp": "2025-04-30 15:32:42"
                },
                {
                    "sender": "银色子弹-捷",
                    "content": "这样的玩具需要联网是必要的，wifi 或者蓝牙 或4G",
                    "timestamp": "2025-04-30 15:33:43"
                },
                {
                    "sender": "tina  ",
                    "content": "是天猫精灵或者小度的迷你版？",
                    "timestamp": "2025-04-30 15:49:02"
                },
                {
                    "sender": "向波",
                    "content": "嗯嗯，比较贵的是电池、大模型云服务、BOM材料、代工费几个部分",
                    "timestamp": "2025-04-30 15:50:52"
                },
                {
                    "sender": "向波",
                    "content": "物联网卡一年几块钱，还好",
                    "timestamp": "2025-04-30 15:51:04"
                },
                {
                    "sender": "银色子弹-捷",
                    "content": "其他都还好，大模型云服务这个可能贵",
                    "timestamp": "2025-04-30 15:52:12"
                },
                {
                    "sender": "虫虫",
                    "content": "想想可能也还好 一个设备 一年能对话多少次 总共tokens消耗量有限 \n\n[引用](2025-04-30 15:52:12)银色子弹-捷:其他都还好，大模型云服务这个可能贵",
                    "timestamp": "2025-04-30 15:57:56"
                },
                {
                    "sender": "tina  ",
                    "content": "这装置，应用在什么上？",
                    "timestamp": "2025-04-30 15:58:56"
                },
                {
                    "sender": "虫虫",
                    "content": "比如毛茸茸玩具[机智]",
                    "timestamp": "2025-04-30 15:59:52"
                },
                {
                    "sender": "兔子先生",
                    "content": "AI小智",
                    "timestamp": "2025-04-30 16:00:44"
                },
                {
                    "sender": "兔子先生",
                    "content": "前段时间非常火",
                    "timestamp": "2025-04-30 16:00:50"
                },
                {
                    "sender": "兔子先生",
                    "content": "卖的非常好",
                    "timestamp": "2025-04-30 16:00:58"
                },
                {
                    "sender": "虫虫",
                    "content": "小智用户还是爱好者",
                    "timestamp": "2025-04-30 16:01:19"
                },
                {
                    "sender": "虫虫",
                    "content": "还没有到终端产品形态",
                    "timestamp": "2025-04-30 16:01:30"
                },
                {
                    "sender": "tina  ",
                    "content": "玩具的用户越来越少，市场也会越来越小\n\n[引用](2025-04-30 15:59:52)虫虫:比如毛茸茸玩具[机智]",
                    "timestamp": "2025-04-30 16:02:14"
                },
                {
                    "sender": "虫虫",
                    "content": "宏观上判断不太准 但是现在市场还是有的",
                    "timestamp": "2025-04-30 16:07:36"
                },
                {
                    "sender": "兔子先生",
                    "content": "不是玩具少，而是你不是他的用户，玩具市场目前逐年上升\n\n[引用](2025-04-30 16:02:14)苏州跨境财务:玩具的用户越来越少，市场也会越来越小",
                    "timestamp": "2025-04-30 16:21:28"
                },
                {
                    "sender": "兔子先生",
                    "content": "图片",
                    "timestamp": "2025-04-30 16:30:30"
                },
                {
                    "sender": "兔子先生",
                    "content": "日不落直播间即将来临[旺柴]",
                    "timestamp": "2025-04-30 16:30:48"
                },
                {
                    "sender": "银色子弹-捷",
                    "content": "我是觉得玩具 接入蓝牙 的方式更实在，其他物联网卡的，我角度看是小众的小众了",
                    "timestamp": "2025-04-30 16:33:08"
                },
                {
                    "sender": "银色子弹-捷",
                    "content": "最大的玩具就是AI家庭机器人，如果这个发展壮大，其他的小玩具就安然失色了",
                    "timestamp": "2025-04-30 16:34:07"
                },
                {
                    "sender": "昏沉沉的",
                    "content": "是的 我了解的也是这样\n\n[引用](2025-04-30 16:21:28):不是玩具少，而是你不是他的用户，玩具市场目前逐年上升",
                    "timestamp": "2025-04-30 16:51:17"
                },
                {
                    "sender": "🌕风林火山.培哲",
                    "content": "Manus邀请码现在还有人要吗",
                    "timestamp": "2025-04-30 17:10:54"
                },
                {
                    "sender": "沙皮狗的忧伤",
                    "content": "有嘛",
                    "timestamp": "2025-04-30 17:11:10"
                },
                {
                    "sender": "🌕风林火山.培哲",
                    "content": "要有魔法上网才行",
                    "timestamp": "2025-04-30 17:11:38"
                },
                {
                    "sender": "🌕风林火山.培哲",
                    "content": "为了激活我科学上网买了一个月",
                    "timestamp": "2025-04-30 17:12:15"
                },
                {
                    "sender": "沙皮狗的忧伤",
                    "content": "🔮我有",
                    "timestamp": "2025-04-30 17:13:06"
                },
                {
                    "sender": "沙皮狗的忧伤",
                    "content": "我填了申请，就没信了",
                    "timestamp": "2025-04-30 17:13:31"
                },
                {
                    "sender": "沙皮狗的忧伤",
                    "content": "去官网",
                    "timestamp": "2025-04-30 17:13:35"
                },
                {
                    "sender": "贾👦🏻",
                    "content": "图片",
                    "timestamp": "2025-04-30 17:13:54"
                },
                {
                    "sender": "贾👦🏻",
                    "content": "来\n\n[引用](2025-04-30 17:10:54)深圳-电脑厂家-培哲:Manus邀请码现在还有人要吗",
                    "timestamp": "2025-04-30 17:13:59"
                },
                {
                    "sender": "贾👦🏻",
                    "content": "\"贾👦🏻\" 拍了拍 \"深圳-电脑厂家-培哲\" 看[胜利]烟花[烟花]",
                    "timestamp": "2025-04-30 17:16:56"
                },
                {
                    "sender": "蜗牛",
                    "content": "我也需要",
                    "timestamp": "2025-04-30 17:17:03"
                },
                {
                    "sender": "贾👦🏻",
                    "content": "扔出来 拼手速 哈哈",
                    "timestamp": "2025-04-30 17:17:18"
                },
                {
                    "sender": "蜗牛",
                    "content": "@深圳-电脑厂家-培哲",
                    "timestamp": "2025-04-30 17:20:05"
                },
                {
                    "sender": "苍何",
                    "content": "视频",
                    "timestamp": "2025-04-30 17:49:27"
                },
                {
                    "sender": "AHapi²⁰²⁵",
                    "content": "图片",
                    "timestamp": "2025-04-30 17:54:37"
                },
                {
                    "sender": "苍何",
                    "content": "这个是显眼包",
                    "timestamp": "2025-04-30 17:57:48"
                },
                {
                    "sender": "昏沉沉的",
                    "content": "hhh",
                    "timestamp": "2025-04-30 17:58:28"
                },
                {
                    "sender": "翟朗博369 ᯤ⁹ᴳ",
                    "content": "@深圳-电脑厂家-培哲 还有吗",
                    "timestamp": "2025-04-30 18:01:03"
                },
                {
                    "sender": "梦ㄆ宇",
                    "content": "[憨笑]",
                    "timestamp": "2025-04-30 18:14:12"
                },
                {
                    "sender": "昏沉沉的",
                    "content": "图片",
                    "timestamp": "2025-04-30 22:24:10"
                }
            ]"""},

        ]


    def process_msg(self,x):
        """
        识别json格式，并返回字典
        """
        pattern = re.compile('{.*}', flags=re.IGNORECASE | re.MULTILINE | re.S)
        # print(pattern.search(json_data).group())

        json_data = json.loads(pattern.search(x).group())
        return json_data




if __name__ == "__main__":
    deepseek_api = DeepSeekApi("sk-2ed4377a895d4ce18e086258c254fc8e")

    response = deepseek_api.send_msg(module=0)
    print(response)











