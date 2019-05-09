import traceback

import jieba
from matplotlib import pyplot
from sklearn.cluster import KMeans, AffinityPropagation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

from multiDimEvents.utils import crawler
from multiDimEvents.models import Event, Article, Category, HotNews
import os

def getStopWords():
    """
        从停用词文件获取停用词列表
        :return stopwordslist:停用词list
        """

    cwd = os.getcwd()
    print("当前工作路径 '%s'" % cwd)# E:\GitHub\thesisWeb
    stopwordpath = "multiDimEvents/stopwords/baidustopwordlist.txt"
    stopword_dic = open(stopwordpath, 'r',encoding='UTF-8')
    stopword_content = stopword_dic.read()
    stopwordslist = stopword_content.splitlines()
    stopword_dic.close()
    return stopwordslist

def cluster(eventname,ishot):
    """
        聚类函数
        :param eventname:事件名称  ishot：是否热点新闻
        """
    articleresults = crawler.crawler(eventname)
    if(articleresults == []):
        return
    dm = [articleresult["title"] + articleresult["content"] for articleresult in articleresults]

    # 将一篇分词后的单词集合重新用空格分开，合成字符串，供tfidfvectorizer进行处理
    data = []
    for line in dm:
        seglist = jieba.cut(line)
        words = " ".join(seglist)
        data.append(words)



    # 参数设置需要注意，如果事件相关文章只有一篇，例如“外国人说“漏电式”东北话走红”则会出问题
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=10000,
                                 min_df=2, stop_words=getStopWords(),
                                 use_idf=True)
    try:
        X = vectorizer.fit_transform(data)
    except:
        traceback.print_exc()
        return

    ''''# 肘方法，绘图
    SSE = []  # 存放每次结果的误差平方和
    for k in range(1, 9):
        estimator = KMeans(n_clusters=k)  # 构造聚类器
        estimator.fit(X)
        SSE.append(estimator.inertia_)
    xxxx = range(1, 9)
    pyplot.xlabel('k')
    pyplot.ylabel('SSE')
    pyplot.plot(xxxx, SSE, 'o-')
    pyplot.show()

    Scores = []  # 存放轮廓系数
    for k in range(2, 19):
        estimator = KMeans(n_clusters=k)  # 构造聚类器
        estimator.fit(X)
        Scores.append(silhouette_score(X,estimator.labels_, metric='euclidean'))
    xxxx = range(2, 19)
    pyplot.xlabel('k')
    pyplot.ylabel('轮廓系数')
    pyplot.plot(xxxx, Scores, 'o-')
    pyplot.show()'''

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
