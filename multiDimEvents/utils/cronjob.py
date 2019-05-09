from multiDimEvents.models import HotNews
from multiDimEvents.utils import crawler, cluster


def getHotNews():
    # 爬取热点事件，聚类并存入数据库
    HotNews.objects.all().delete()# 清空hotnews
    eventnames = crawler.crawlHotNews()
    print(eventnames)
    # 因为这个不急，就不用多进程了
    for eventname in eventnames:
        cluster.cluster(eventname,True)