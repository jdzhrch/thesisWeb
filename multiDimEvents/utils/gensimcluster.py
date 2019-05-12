# coding:utf-8

import sys
import gensim
import jieba
import numpy as np

from gensim.models.doc2vec import Doc2Vec, LabeledSentence
from sklearn.cluster import KMeans

from multiDimEvents.utils import crawler

TaggededDocument = gensim.models.doc2vec.TaggedDocument

def get_datasest():
    articleresults = crawler.crawler(eventname)
    if (articleresults == []):
        return
    articles = [articleresult["title"] + articleresult["content"] for articleresult in articleresults]

    x_train = []
    #y = np.concatenate(np.ones(len(docs)))
    for i, text in enumerate(articles):
        word_list = jieba.cut(text)
        l = len(word_list)
        word_list[l-1] = word_list[l-1].strip()
        document = TaggededDocument(word_list, tags=[i])
        x_train.append(document)

    return x_train


def cluster(x_train, size=200, epoch_num=1):
    model_dm = Doc2Vec(x_train, min_count=1, window=3, size=size, sample=1e-3, negative=5, workers=4)
    model_dm.train(x_train, total_examples=model_dm.corpus_count, epochs=100)
    infered_vectors_list = []
    i = 0
    for text, label in x_train:
        vector = model_dm.infer_vector(text)
        infered_vectors_list.append(vector)
        i += 1

    kmean_model = KMeans(n_clusters=15)
    kmean_model.fit(infered_vectors_list)
    labels= kmean_model.predict(infered_vectors_list[0:100])
    cluster_centers = kmean_model.cluster_centers_

    return cluster_centers




if __name__ == '__main__':
    x_train = get_datasest()
    model_dm = train(x_train)
    cluster_centers = cluster(x_train)