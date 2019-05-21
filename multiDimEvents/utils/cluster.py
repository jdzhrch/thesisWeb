import traceback
from sklearn.cluster import KMeans, AffinityPropagation
from sklearn.decomposition import LatentDirichletAllocation

from multiDimEvents.models import Event, Article, Category, HotNews
from multiDimEvents.utils import crawler, myvectorizer
import numpy as np

from multiDimEvents.utils.clusterEvaluater import clusterEvaluate


def cluster(eventname, ishot, method):
    """
        聚类函数
        :param method: 聚类算法
        :param ishot: 是否热点新闻
        :param eventname:事件名称  ishot：是否热点新闻
        """
    articleresults = crawler.crawler(eventname)
    if (articleresults == []):
        return
    articles = [articleresult["title"] + articleresult["content"] for articleresult in articleresults]

    # vectorizeLDAsklearn(articles)
    # 向量化，bow模型
    try:
        X, terms = myvectorizer.vectorizeBOW(articles, "tfidf")
        # X = myvectorizer.vectorizeDOCTOVEC(articles)
    except:
        traceback.print_exc()
        return

    # clusterEvaluate(X,"silhouette coefficient")
    # clusterEvaluate(X, "elbow")

    # 聚类算法
    if method == "kmeans":
        #n_cluster = 6
        clusterAlgorithm = AffinityPropagation(preference=-3).fit(X)  # preference在-5到-3之间表现较好
        n_cluster = len(clusterAlgorithm.cluster_centers_indices_)
        clusterAlgorithm = KMeans(n_clusters=n_cluster, init='k-means++', max_iter=100, n_init=1).fit(X)
        order_centroids = clusterAlgorithm.cluster_centers_.argsort()[:, ::-1]
    elif method == "ap":
        clusterAlgorithm = AffinityPropagation(preference=-3).fit(X)  # preference在-5到-3之间表现较好
        n_cluster = len(clusterAlgorithm.cluster_centers_indices_)
        order_centroids_tmp = clusterAlgorithm.cluster_centers_.toarray()
        order_centroids = order_centroids_tmp.argsort()[:, ::-1]
    eventname += method
    print(clusterAlgorithm.labels_)

    ''' 
        以下数据持久化处理，用于前端展示
    '''
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
    if (ishot):
        hotNews = HotNews(eventId=event)
        hotNews.save()
    # category写入数据库
    categories = []  # category列表，用于作为article的外键
    for i in range(n_cluster):
        print("Cluster %d:" % i, end='')
        featurelist = terms[order_centroids[i, :10][0]]
        termno = 1
        for termno in range(9):
            termno += 1
            print(' %s' % terms[order_centroids[i, :10][termno]], end='')
            # 每行展示两个关键词
            if termno % 2 != 0:
                featurelist = featurelist + " " + terms[order_centroids[i, :10][termno]]
            else:
                featurelist = featurelist + "\n" + terms[order_centroids[i, :10][termno]]
            termno += 1
            # featurelist = featurelist + "+" + "doc2vec特征" + str(i) + "\n"
        print()
        category = Category(eventId=event, featureList=featurelist, reportVer=1, articleNum=articleNumDict[i])
        category.save()
        categories.append(category)

    # article写入数据库
    label_index = 0  # clusterAlgorithm.labels的index
    for articleresult in articleresults:
        article = Article(categoryId=categories[clusterAlgorithm.labels_[label_index]], title=articleresult['title'],
                          content=articleresult['content'], url=articleresult["webpageUrl"],
                          published=articleresult["published"])
        article.save()
        label_index = label_index + 1


def clusterLDA(eventname, ishot, method):
    """
        聚类函数
        :param method: 聚类算法
        :param ishot: 是否热点新闻
        :param eventname:事件名称  ishot：是否热点新闻
        """
    articleresults = crawler.crawler(eventname)
    if (articleresults == []):
        return
    articles = [articleresult["title"] + articleresult["content"] for articleresult in articleresults]

    # 向量化，bow模型
    try:
        X, terms = myvectorizer.vectorizeBOW(articles, "count")
        # X = myvectorizer.vectorizeDOCTOVEC(articles)
    except:
        traceback.print_exc()
        return

    # clusterEvaluate(X,"elbow")

    # 聚类算法
    '''n_cluster = 4
    clusterAlgorithm = KMeans(n_clusters=n_cluster, init='k-means++', max_iter=100, n_init=1).fit(X)
    order_centroids=clusterAlgorithm.cluster_centers_.argsort()[:, ::-1]'''
    '''clusterAlgorithm = AffinityPropagation().fit(X)  # preference在-5到-3之间表现较好
    n_cluster = len(clusterAlgorithm.cluster_centers_indices_)
    order_centroids_tmp = clusterAlgorithm.cluster_centers_#.toarray()
    order_centroids = order_centroids_tmp.argsort()[:, ::-1]
    print(clusterAlgorithm.labels_)'''

    n_cluster = 7
    lda = LatentDirichletAllocation(n_components=n_cluster,
                                    learning_offset=50.,
                                    random_state=0)
    docres = lda.fit_transform(X)
    components = lda.components_
    doc_maxtopic_list = []
    for doc_topics_list in docres:
        secondmaxindex = np.argsort(doc_topics_list)[-1]
        doc_maxtopic_list.append(secondmaxindex)
    print(doc_maxtopic_list)
    ''' 
        以下数据持久化处理，用于前端展示
    '''
    # 每个cluster的article数对应关系
    articleNumDict = [0] * n_cluster
    for label in doc_maxtopic_list:  # for label in clusterAlgorithm.labels_:  # label是数字，cluster的id
        articleNumDict[label] += 1

    # event写入数据库
    event = Event(eventName=eventname + "lda", reportVer=1, categoryNum=n_cluster, searchNum=1)
    event.save()
    if (ishot):
        hotNews = HotNews(eventId=event)
        hotNews.save()
    # category写入数据库
    categories = []  # category列表，用于作为article的外键
    for i in range(n_cluster):
        print("Cluster %d:" % i, end='')
        featurelist = ""
        termindexes = np.argpartition(components[i], -10)[-10:]
        featurelist = terms[termindexes[0]]
        for termno in range(9):
            termno += 1
            print(' %s' % terms[termindexes[termno]], end='')
            # 每行展示两个关键词
            if termno % 2 != 0:
                featurelist = featurelist + " " + terms[termindexes[termno]]
            else:
                featurelist = featurelist + "\n" + terms[termindexes[termno]]
        '''for ind in order_centroids[i, :10]:
            #print(' %s' % terms[ind], end='')
            #if i % 3 != 0:
                featurelist = featurelist + " " + terms[ind]
            elif i != 0:
                featurelist = featurelist + "\n" + terms[ind]
            featurelist = featurelist + "+" + "doc2vec特征" + str(i) + "\n"'''
        print()
        category = Category(eventId=event, featureList=featurelist, reportVer=1, articleNum=articleNumDict[i])
        category.save()
        categories.append(category)

    # article写入数据库
    label_index = 0  # clusterAlgorithm.labels的index
    for articleresult in articleresults:
        # article = Article(categoryId=categories[clusterAlgorithm.labels_[label_index]], title=articleresult['title'],
        #                 content=articleresult['content'], url=articleresult["webpageUrl"],
        #                 published=articleresult["published"])
        article = Article(categoryId=categories[doc_maxtopic_list[label_index]], title=articleresult['title'],
                          content=articleresult['content'], url=articleresult["webpageUrl"],
                          published=articleresult["published"])
        article.save()
        label_index = label_index + 1
