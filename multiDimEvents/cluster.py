import jieba
from sklearn.cluster import KMeans, AffinityPropagation
from sklearn.feature_extraction.text import TfidfVectorizer
import pymysql


def to_cut_chinese(dm: list) -> list:
    """
    将数据源中的中文文本分词后以空格连接，用于sklearn的分词
    :param dm: str的list，每个str是一个article的content
    :return: numpy形式的词语-文本矩阵
    """
    mysql = pymysql.connect("localhost", "root", "mysqldatabase", "corpus", charset='utf8')
    cursor = mysql.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT `title`, `content` FROM `news` limit 10")
    dm = [c["title"] + c["content"] for c in cursor.fetchall()]

    data = []
    f = dm
    for line in f:
        seglist = jieba.cut(line)
        words = " ".join(seglist)
        data.append(words)
    return data

def cluster(dm: list):
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=5,
                                 min_df=2, stop_words='english',
                                 use_idf=True)
    X = vectorizer.fit_transform(to_cut_chinese(dm))
    dictionary = dict(zip(vectorizer.vocabulary_.values(), vectorizer.vocabulary_.keys()))
    # km = KMeans(n_clusters=4, init='k-means++', max_iter=100, n_init=1)
    af = AffinityPropagation().fit(X)
    n_cluster = len(af.cluster_centers_indices_)
    order_centroids_tmp = af.cluster_centers_.toarray()
    order_centroids = order_centroids_tmp.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()
    for i in range(n_cluster):
        print("Cluster %d:" % i, end='')
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind], end='')
        print()
    print(af.labels_)