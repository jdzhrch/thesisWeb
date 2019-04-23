import re

import requests


def getRidOfTag(originStr):
    """
        去除html标签
        :param originStr: 未去除html标签的原始字符串
        :return: 去除了html标签的字符串
    """
    # 定义script的正则表达式，去除js可以防止注入
    scriptRegex = "<script[^>]*?>[\\s\\S]*?<\\/script>"
    strNoJs = re.sub(scriptRegex, "", originStr)
    # 定义style的正则表达式，去除style样式，防止css代码过多时只截取到css样式代码
    styleRegex = "<style[^>]*?>[\\s\\S]*?<\\/style>"
    strNoStyle = re.sub(styleRegex, "", strNoJs)
    # 定义HTML标签的正则表达式，去除标签，只提取文字内容
    htmlRegex = "<[^>]+>"
    strNoTag = re.sub(htmlRegex, "", strNoStyle)
    return strNoTag


def crawler(eventname):
    params = {
        'format': 'json',
        'keyword': eventname,
        'num': 100,
        'fromtype': 7,
    }
    response = requests.get("http://58.16.248.132:8080/comm_api/search", params=params)
    print(response.json())
    articleresults = response.json()
    # 去除爬下来的文本中无用的标签等
    for articleresult in articleresults:
        articleresult["title"] = getRidOfTag(articleresult["title"])
        articleresult["content"] = getRidOfTag(articleresult["content"])
    return articleresults