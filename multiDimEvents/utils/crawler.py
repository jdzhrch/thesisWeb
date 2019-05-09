import multiprocessing
import re
import time
from multiprocessing import Pool

import requests
from multiDimEvents.utils.news import captureNews


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


def crawlerapi(eventname):
    params = {
        'format': 'json',
        'keyword': eventname,
        'num': 100,
        'fromtype': 7,
    }
    response = requests.get("http://58.16.248.132:8080/comm_api/search", params=params)
    articleresults = response.json()
    # 去除爬下来的文本中无用的标签等
    for articleresult in articleresults:
        articleresult["title"] = getRidOfTag(articleresult["title"])
        articleresult["content"] = getRidOfTag(articleresult["content"])
    return articleresults


def crawlHotNews():
    # 1. download baidu news
    hub_url = 'http://news.baidu.com/'
    res = requests.get(hub_url)
    html = res.text

    # 2. 取出搜索热点
    eventnames = re.findall(r'target="_blank" class="hotwords_li_a" title=[\'"]?(.*?)[\'"\s]', html)
    '''切词
    eventnamesCut = []
    for eventname in eventnames:
        keyList = jieba.cut(eventname)
        eventnameCut = "+".join(keyList)
        eventnamesCut.append(eventnameCut)
    return eventnamesCut'''
    return eventnames


def crawler(eventname):
    oldtime = time.time()
    articleresults = multiprocessing.Manager().list()
    # 每页开一个进程去爬
    pagenumber = 10
    pool = Pool(processes=pagenumber)
    for pn in range(pagenumber):
        baiduUrl = "https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word="+ eventname +"&pn="+ str(pn * 10)
        pool.apply_async(captureNews,(baiduUrl,articleresults))
    pool.close()
    pool.join()
    for articleresult in articleresults:
        articleresult["title"] = getRidOfTag(articleresult["title"])
        articleresult["content"] = getRidOfTag(articleresult["content"])
    '''
    articleresults = []
    for pn in range(10):
        baiduUrl = "https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word=" + eventname + "&pn=" + str(
            pn * 10)
        captureNews(baiduUrl, articleresults)
    for articleresult in articleresults:
        articleresult["title"] = getRidOfTag(articleresult["title"])
        articleresult["content"] = getRidOfTag(articleresult["content"])'''
    print("花的秒数",time.time()-oldtime)
    return articleresults