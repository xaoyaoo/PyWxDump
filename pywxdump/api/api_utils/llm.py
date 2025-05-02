# LLM api相关
import enum
import json
import os
import re

import httpx
import openai
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
        """
        要确保message中至少有两个元素，第一个元素为系统消息，第二个元素为用户消息，且第二个元素中有{{content}}
        """
        self.message = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello {{content}}"},
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
            self.message[1]["content"] = self.message[1].get("content").replace("{{content}}", " ")
            message = self.message
        else:
            self.message[1]["content"] = self.message[1].get("content").replace("{{content}}", message)
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
            {"role": "user", "content": """你好，以下是我要提取的内容: {{content}}"""},

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

    response = deepseek_api.send_msg(module=0,message="""""")
    print(response)











