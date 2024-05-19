# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parsingFavorite.py
# Description:  
# Author:       xaoyaoo
# Date:         2024/05/18
# -------------------------------------------------------------------------------
import pandas as pd

from .dbbase import DatabaseBase
from .utils import timestamp2str, xml2dict


# * FavItems：收藏的消息条目列表
# * FavDataItem：收藏的具体数据。大概可以确定以下两点
#     * 即使只是简单收藏一篇公众号文章也会在 FavDataItem 中有一个对应的记录
#     * 对于收藏的合并转发类型的消息，合并转发中的每一条消息在 FavDataItem 中都是一个独立的记录
# * FavTags：为收藏内容添加的标签


def FavoriteTypeId2Name(Type):
    TypeNameDict = {
        1: "文本",  # 文本 已测试
        2: "图片",  # 图片 已测试
        3: "语音",  # 语音
        4: "视频",  # 视频 已测试
        5: "链接",  # 链接 已测试
        6: "位置",  # 位置
        7: "小程序",  # 小程序
        8: "文件",  # 文件 已测试
        14: "聊天记录",  # 聊天记录 已测试
        16: "群聊视频",  # 群聊中的视频 可能
        18: "笔记"  # 笔记 已测试
    }
    return TypeNameDict.get(Type, "未知")


class ParsingFavorite(DatabaseBase):
    _class_name = "Favorite"

    def __init__(self, db_path):
        super().__init__(db_path)

    def get_tags(self, LocalID):
        """
        return: {LocalID: TagName}
        """
        if LocalID is None:
            sql = "select LocalID, TagName from FavTagDatas order by ServerSeq"
        else:
            sql = "select LocalID, TagName from FavTagDatas where LocalID = '%s' order by ServerSeq " % LocalID
        tags = self.execute_sql(sql)  # [(1, 797940830, '程序语言类'), (2, 806153863, '账单')]
        # 转换为字典
        tags = {tag[0]: tag[1] for tag in tags}
        return tags

    def get_FavBindTags(self):
        """
        return: [(FavLocalID, TagName)]
        """
        sql = "select A.FavLocalID, B.TagName from FavBindTagDatas A, FavTagDatas B where A.TagLocalID = B.LocalID"
        FavBindTags = self.execute_sql(sql)
        return FavBindTags

    def get_favorite(self):
        """
        return: [{FavItemsFields}, {FavItemsFields}]
        """
        FavItemsFields = {
            "FavLocalID": "本地收藏ID",
            "SvrFavId": "服务器收藏ID",
            "SourceId": "源ID",
            "Type": "类型",
            "SourceType": "源类型",
            "LocalStatus": "本地状态",
            "Flag": "标记",
            "Status": "状态",
            "FromUser": "源用户",
            "RealChatName": "实际聊天名称",
            "SearchKey": "搜索关键字",
            "UpdateTime": "更新时间",
            "reseverd0": "预留字段0",
            "XmlBuf": "XML缓冲区"
        }
        FavDataItemFields = {
            "FavLocalID": "本地收藏ID",
            "Type": "类型",
            "DataId": "数据ID",
            "HtmlId": "HTML ID",
            "Datasourceid": "数据源ID",
            "Datastatus": "数据状态",
            "Datafmt": "数据格式",
            "Datatitle": "数据标题",
            "Datadesc": "数据描述",
            "Thumbfullmd5": "缩略图全MD5",
            "Thumbhead256md5": "缩略图头256MD5",
            "Thumbfullsize": "缩略图全尺寸",
            "fullmd5": "全MD5",
            "head256md5": "头256MD5",
            "fullsize": "全尺寸",
            "cdn_thumburl": "CDN缩略图URL",
            "cdn_thumbkey": "CDN缩略图KEY",
            "thumb_width": "缩略图宽度",
            "thumb_height": "缩略图高度",
            "cdn_dataurl": "CDN数据URL",
            "cdn_datakey": "CDN数据KEY",
            "cdn_encryver": "CDN加密版本",
            "duration": "时长",
            "stream_weburl": "流媒体WEB URL",
            "stream_dataurl": "流媒体数据URL",
            "stream_lowbandurl": "流媒体低带宽URL",
            "sourcethumbpath": "源缩略图路径",
            "sourcedatapath": "源数据路径",
            "stream_videoid": "流媒体视频ID",
            "Rerserved1": "保留字段1",
            "Rerserved2": "保留字段2",
            "Rerserved3": "保留字段3",
            "Rerserved4": "保留字段4",
            "Rerserved5": "保留字段5",
            "Rerserved6": "保留字段6",
            "Rerserved7": "保留字段7"
        }

        sql1 = "select " + ",".join(FavItemsFields.keys()) + " from FavItems order by UpdateTime desc"
        sql2 = "select " + ",".join(FavDataItemFields.keys()) + " from FavDataItem B order by B.RecId asc"

        FavItemsList = self.execute_sql(sql1)
        FavDataItemList = self.execute_sql(sql2)
        if FavItemsList is None or len(FavItemsList) == 0:
            return False

        FavDataDict = {}
        if FavDataItemList and len(FavDataItemList) >= 0:
            for item in FavDataItemList:
                data_dict = {}
                for i, key in enumerate(FavDataItemFields.keys()):
                    data_dict[key] = item[i]
                FavDataDict[item[0]] = FavDataDict.get(item[0], []) + [data_dict]
        # 获取标签
        FavTags = self.get_FavBindTags()
        FavTagsDict = {}
        for FavLocalID, TagName in FavTags:
            FavTagsDict[FavLocalID] = FavTagsDict.get(FavLocalID, []) + [TagName]

        pf = pd.DataFrame(FavItemsList)
        pf.columns = FavItemsFields.keys()  # set column names
        pf["UpdateTime"] = pf["UpdateTime"].apply(timestamp2str)  # 处理时间
        pf["XmlBuf"] = pf["XmlBuf"].apply(xml2dict)  # 处理xml
        pf["TypeName"] = pf["Type"].apply(FavoriteTypeId2Name)  # 添加类型名称列
        pf["FavData"] = pf["FavLocalID"].apply(lambda x: FavDataDict.get(x, []))  # 添加数据列
        pf["Tags"] = pf["FavLocalID"].apply(lambda x: FavTagsDict.get(x, []))  # 添加标签列
        pf = pf.fillna("")  # 去掉Nan
        rdata = pf.to_dict(orient="records")
        return rdata
