import heapq

import gensim
import jieba
import os

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from gensim.models.doc2vec import Doc2Vec, LabeledSentence
import numpy as np
TaggededDocument = gensim.models.doc2vec.TaggedDocument


def getStopWords():
    """
        从停用词文件获取停用词列表
        :return stopwordslist:停用词list
        """
    cwd = os.getcwd()
    print("当前工作路径 '%s'" % cwd)  # E:\GitHub\thesisWeb
    stopwordpath = "multiDimEvents/stopwords/baidustopwordlist.txt"
    stopword_dic = open(stopwordpath, 'r', encoding='UTF-8')
    stopword_content = stopword_dic.read()
    stopwordslist = stopword_content.splitlines()
    stopword_dic.close()
    return stopwordslist


def vectorizeBOW(articles):
    """
        采用bog模型对文档集进行向量化
        目前用的是tfidf
        :param articles:文章的list
        :return X:文章转换后的向量矩阵
                terms:特征词与序号的对应关系，用于调出前十个特征词展示出来
        """
    # 将一篇分词后的单词集合重新用空格分开，合成字符串，供tfidfvectorizer进行处理
    data = []
    for article in articles:
        seglist = jieba.cut(article)
        words = " ".join(seglist)
        data.append(words)

    # 参数设置需要注意，如果事件相关文章只有一篇，例如“外国人说“漏电式”东北话走红”则会出问题
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=10000,
                                 min_df=2, stop_words=getStopWords(),
                                 use_idf=True)
    X = vectorizer.fit_transform(data)
    terms = vectorizer.get_feature_names()
    # dictionary = dict(zip(vectorizer.vocabulary_.values(), vectorizer.vocabulary_.keys()))
    return X, terms


def vectorizeDOCTOVEC(articles):
    """
        采用doc2vec模型对文档集进行向量化
        :param articles:文章的list
        :return X:文章转换后的向量矩阵
        """
    # doc2vec
    x_train = []
    # y = np.concatenate(np.ones(len(docs)))
    for i, text in enumerate(articles):
        word_list = jieba.__lcut(text)
        l = len(word_list)
        word_list[l - 1] = word_list[l - 1].strip()
        document = TaggededDocument(word_list, tags=[i])
        x_train.append(document)
    model_dm = Doc2Vec(x_train, min_count=1, window=3, vector_size=200, sample=1e-3, negative=5, workers=4)
    print("训练开始")
    model_dm.train(x_train, total_examples=model_dm.corpus_count, epochs=100)
    print("训练结束")
    X = []
    i = 0
    for text, label in x_train:
        vector = model_dm.infer_vector(text)
        X.append(vector)
        i += 1
    return X

def vectorizeLDAgensim(articles):
    common_texts = []
    for article in articles:
        seglist = jieba.__lcut(article)
        common_texts.append(seglist)
    dic = gensim.corpora.Dictionary(common_texts)
    corpus = [dic.doc2bow(text) for text in common_texts]

    tfidf = gensim.models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    lda = gensim.models.LdaModel(corpus_tfidf, id2word=dic, num_topics=20, alpha='auto')
    corpus_lda = lda[corpus_tfidf]
    print(corpus_lda)

def vectorizeLDAsklearn(articles):
    data = []
    for article in articles:
        seglist = jieba.cut(article)
        words = " ".join(seglist)
        data.append(words)

    # 参数设置需要注意，如果事件相关文章只有一篇，例如“外国人说“漏电式”东北话走红”则会出问题
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=10000,
                                 min_df=2, stop_words=getStopWords(),
                                 use_idf=True)
    X = vectorizer.fit_transform(data)
    terms = vectorizer.get_feature_names()

    n_cluster = 4
    lda = LatentDirichletAllocation(n_topics=n_cluster,
                                    learning_offset=50.,
                                    random_state=0)
    docres = lda.fit_transform(X)
    components = lda.components_
    doc_maxtopic_list = []
    for doc_topics_list in docres:
        doc_maxtopic_list.append(np.argmax(doc_topics_list))
    print(doc_maxtopic_list)
    for i in range(n_cluster):
        termindexes = np.argpartition(components[i], -10)[-10:]
        print("Cluster %d:" % i, end='')
        for ind in termindexes:
            print(' %s' % terms[ind], end='')