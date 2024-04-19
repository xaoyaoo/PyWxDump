import logging


def ReJson(code: int, body: [dict, list] = None, msg: str = None, error: str = None, extra: dict = None) -> dict:
    """
        返回格式化的json数据
    :param code: 状态码  int
    :param body: 返回的主体内容，一般为具体的数据
    :param msg: 返回状态码相关的调试信息
    :param error: 出现错误时候,这个参数可以把错误写入日志
    :param extra: # 全局附加数据，字段、内容不定（如等级，经验的变化，可以作为全局的数据存在，区别于某次请求的具体data）
    :return: json格式的返回值
    """
    if extra is None:
        extra = {}
    situation = {
        0: {'code': 0, 'body': body, 'msg': "success", "extra": extra},
        # 100 开头代表 请求数据有问题
        # 4*** 表示数据库查询结果存在异常
        1001: {'code': 1001, 'body': body, 'msg': "请求数据格式存在错误！", "extra": extra}, # 请求数据格式存在错误，一般是数据类型错误
        1002: {'code': 1002, 'body': body, 'msg': "请求参数存在错误！", "extra": extra},  # 请求参数存在错误,一般是缺少参数
        2001: {'code': 2001, 'body': body, 'msg': "操作失败！", "extra": extra},  # 请求未能正确执行
        4001: {'code': 4001, 'body': body, 'msg': "账号或密码错误！", "extra": extra},  # 表示用户没有权限（令牌、用户名、密码错误）
        4003: {'code': 4003, 'body': body, 'msg': "禁止访问！", "extra": extra},
        4004: {'code': 4004, 'body': body, 'msg': "数据不存在！", "extra": extra},
        4005: {'code': 4005, 'body': body, 'msg': "数据库异常！", "extra": extra},
        4006: {'code': 4006, 'body': body, 'msg': "数据已存在！", "extra": extra},
        4007: {'code': 4007, 'body': body, 'msg': "数据库解密异常！", "extra": extra},
        5002: {'code': 5002, 'body': body, 'msg': "服务器错误！", "extra": extra},
        9999: {'code': 9999, 'body': body, 'msg': "未知错误！", "extra": extra},
    }
    rjson = situation.get(code, {'code': 9999, 'body': None, 'msg': "code错误", "extra": {}})
    if code != 0:
        logging.warning(f"\n{code} \n{rjson['body']}\n{msg if msg else None}")
    if body:
        rjson['body'] = body
    if msg:
        rjson['msg'] = msg
    if error:
        logging.error(error)
    return rjson


def RqJson(rqData):
    """
    进行请求数据验证数据合法性，确实用户以及资格
    主要根路径下的数据
    :param rqData: 请求的数据
    :return: body的值
    """
    userid = rqData.get("userid", "")  # 用户id
    version = rqData.get("version", "v1.0")  # api版本
    uidid = rqData.get("uidid", "qweqrew")  # 唯一设备标识符
    token = rqData.get("token", "")  # token
    """验证数据合法性"""
    """"""
    body = rqData.get("body", None)
    return body


if __name__ == '__main__':
    print(ReJson(0, "asdf", "asdf"))
