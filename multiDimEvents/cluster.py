import re

import jieba
import requests
from sklearn.cluster import KMeans, AffinityPropagation
from sklearn.feature_extraction.text import TfidfVectorizer
import pymysql

from multiDimEvents import crawler
from multiDimEvents.models import Event, Article, Category, HotNews

'''
def to_cut_chinese(dm: list) -> list:
    """
    将数据源中的中文文本分词后以空格连接，用于sklearn的分词
    :param dm: str的list，每个str是一个article的content
    :return: numpy形式的词语-文本矩阵
    """
    # 以下应该用爬虫替代
    mysql = pymysql.connect("localhost", "root", "mysqldatabase", "corpus", charset='utf8')
    cursor = mysql.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT `title`, `content` FROM `news` limit 10")
    dm = [c["title"] + c["content"] for c in cursor.fetchall()]

    # 将event写入数据库
    event = Event(eventName="荷兰飞机失事",reportVer=1,categoryNum=0,searchNum=1)
    event.save()
    eventid = event.id

    # 将一篇分词后的单词集合重新用空格分开，合成字符串，供sklearn调用的接口进行处理
    data = []
    for line in dm:
        seglist = jieba.cut(line)
        words = " ".join(seglist)
        data.append(words)
    return data
'''


def cluster(eventname,ishot):
    """
        聚类函数
        :param eventname:事件名称  ishot：是否热点新闻
        """
    articleresults = crawler.crawler(eventname)
    if(articleresults == []):
        return
    dm = [articleresult["title"] + articleresult["content"] for articleresult in articleresults]

    # 以下应该用爬虫替代
    '''mysql = pymysql.connect("localhost", "root", "mysqldatabase", "corpus", charset='utf8')
    cursor = mysql.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT `title`, `content` FROM `news` limit 10")
    dm = [c["title"] + c["content"] for c in cursor.fetchall()]
    cursor.execute("SELECT  `url`, `title`, `content` FROM `news` limit 10")# 注意cursor的用法
'''

    # 将一篇分词后的单词集合重新用空格分开，合成字符串，供tfidfvectorizer进行处理
    data = []
    for line in dm:
        seglist = jieba.cut(line)
        words = " ".join(seglist)
        data.append(words)

    # 参数设置需要注意，如果事件相关文章只有一篇，例如“外国人说“漏电式”东北话走红”则会出问题
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=10000,
                                 min_df=2, stop_words='english',
                                 use_idf=True)
    try:
        X = vectorizer.fit_transform(data)
    except:
        return
    dictionary = dict(zip(vectorizer.vocabulary_.values(), vectorizer.vocabulary_.keys()))
    '''n_cluster = 4
    clusterAlgorithm = KMeans(n_clusters=n_cluster, init='k-means++', max_iter=100, n_init=1)
    clusterAlgorithm.fit(X)
    order_centroids=clusterAlgorithm.cluster_centers_.argsort()[:, ::-1]'''
    clusterAlgorithm = AffinityPropagation(preference=-4.4).fit(X)# preference在-5到-3之间表现较好
    n_cluster = len(clusterAlgorithm.cluster_centers_indices_)
    order_centroids_tmp = clusterAlgorithm.cluster_centers_.toarray()
    order_centroids = order_centroids_tmp.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()

    # 每个cluster的article数对应关系
    articleNumDict = {}
    for label in clusterAlgorithm.labels_:  # label是数字，cluster的id
        if label in articleNumDict.keys():
            articleNumDict[label] = articleNumDict[label] + 1
        else:
            articleNumDict[label] = 0

    # event写入数据库
    event = Event(eventName=eventname, reportVer=1, categoryNum=n_cluster, searchNum=1)
    event.save()
    if(ishot):
        hotNews = HotNews(eventId=event)
        hotNews.save()
    # category写入数据库
    categories = []# category列表，用于作为article的外键
    for i in range(n_cluster):
        print("Cluster %d:" % i, end='')
        featurelist = ""
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind], end='')
            featurelist = featurelist + "+" + terms[ind]+"\n"
        print()
        category = Category(eventId=event, featureList=featurelist, reportVer=1, articleNum=articleNumDict[i])
        category.save()
        categories.append(category)
    print(clusterAlgorithm.labels_)

    # article写入数据库
    label_index = 0  # clusterAlgorithm.labels的index
    for articleresult in articleresults:
        article = Article(categoryId=categories[clusterAlgorithm.labels_[label_index]], title=articleresult['title'],
                          content=articleresult['content'], url=articleresult["webpageUrl"], published=articleresult["published"])
        article.save()
        label_index = label_index + 1

'''
    for c in cursor.fetchall():
        article = Article(categoryId=categories[clusterAlgorithm.labels_[label_index]],title=c['title'], content=c['content'], url=c["url"], published=300)  # article是否需要pv
        article.save()
        label_index = label_index+1
'''
