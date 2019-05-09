import traceback

import jieba
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from multiDimEvents.utils import crawler
from multiDimEvents.utils.cluster import getStopWords
import matplotlib.pyplot as plt
articleresults = crawler.crawler("李彦宏")
dm = [articleresult["title"] + articleresult["content"] for articleresult in articleresults]

data = []
for line in dm:
    seglist = jieba.cut(line)
    words = " ".join(seglist)
    data.append(words)

vectorizer = TfidfVectorizer(max_df=0.5, max_features=10000,
                             min_df=2, stop_words=getStopWords(),
                             use_idf=True)
try:
    X = vectorizer.fit_transform(data)
except:
    traceback.print_exc()

SSE = []  # 存放每次结果的误差平方和
for k in range(1, 9):
    estimator = KMeans(n_clusters=k)  # 构造聚类器
    estimator.fit(X)
    SSE.append(estimator.inertia_)
X = range(1, 9)
plt.xlabel('k')
plt.ylabel('SSE')
plt.plot(X, SSE, 'o-')
plt.show()