import re

import jieba
import requests
from sklearn.cluster import KMeans, AffinityPropagation
from sklearn.feature_extraction.text import TfidfVectorizer
import pymysql

from multiDimEvents import crawler
from multiDimEvents.models import Event, Article, Category

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


def cluster(eventname):
    """
        将数据源中的中文文本分词后以空格连接，用于sklearn的分词
        :param dm: str的list，每个str是一个article的content
        :return: numpy形式的词语-文本矩阵
        """
    articleresults = crawler.crawler(eventname)
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

    vectorizer = TfidfVectorizer(max_df=0.5, max_features=10000,
                                 min_df=2, stop_words='english',
                                 use_idf=True)
    X = vectorizer.fit_transform(data)
    dictionary = dict(zip(vectorizer.vocabulary_.values(), vectorizer.vocabulary_.keys()))
    # km = KMeans(n_clusters=4, init='k-means++', max_iter=100, n_init=1)
    af = AffinityPropagation().fit(X)
    n_cluster = len(af.cluster_centers_indices_)
    order_centroids_tmp = af.cluster_centers_.toarray()
    order_centroids = order_centroids_tmp.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()

    # 每个cluster的article数对应关系
    articleNumDict = {}
    for label in af.labels_:  # label是数字，cluster的id
        if label in articleNumDict.keys():
            articleNumDict[label] = articleNumDict[label] + 1
        else:
            articleNumDict[label] = 0

    # event写入数据库
    event = Event(eventName=eventname, reportVer=1, categoryNum=n_cluster, searchNum=1)
    event.save()
    # category写入数据库
    categories = []
    for i in range(n_cluster):
        print("Cluster %d:" % i, end='')
        featurelist = ""
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind], end='')
            featurelist = featurelist + " " + terms[ind]
        print()
        category = Category(eventId=event, featureList=featurelist, reportVer=1, articleNum=articleNumDict[i])
        category.save()
        categories.append(category)
    print(af.labels_)

    # article写入数据库
    label_index = 0  # af.labels的index
    for articleresult in articleresults:
        article = Article(categoryId=categories[af.labels_[label_index]], title=articleresult['title'],
                          content=articleresult['content'], url=articleresult["webpageUrl"], pv=300)
        article.save()
        label_index = label_index + 1

'''
    for c in cursor.fetchall():
        article = Article(categoryId=categories[af.labels_[label_index]],title=c['title'], content=c['content'], url=c["url"], pv=300)  # 这里pv需要修改
        article.save()
        label_index = label_index+1
'''
