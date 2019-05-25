from sklearn.cluster import KMeans
from matplotlib import pyplot
from sklearn.metrics import silhouette_score
from sqlalchemy.dialects.mysql import pymysql


def clusterEvaluate(X, method):
    """
        用于评估聚类效果，或者确定簇数
        :param X:文章的向量矩阵
                method:采用哪种方法评估
        """
    if method == "elbow":
        # 肘方法，绘图
        SSE = []  # 存放每次结果的误差平方和
        for k in range(1, 30):
            estimator = KMeans(n_clusters=k)  # 构造聚类器
            estimator.fit(X)
            SSE.append(estimator.inertia_)
        xxxx = range(1, 30)
        pyplot.xlabel('k')
        pyplot.ylabel('SSE')
        pyplot.plot(xxxx, SSE, 'o-')
        pyplot.show()
    elif method == "silhouette coefficient":
        Scores = []  # 存放轮廓系数
        for k in range(2, 30):
            estimator = KMeans(n_clusters=k)  # 构造聚类器
            estimator.fit(X)
            Scores.append(silhouette_score(X, estimator.labels_, metric='euclidean'))
        xxxx = range(2, 30)
        pyplot.xlabel('k')
        pyplot.ylabel('轮廓系数')
        pyplot.plot(xxxx, Scores, 'o-')
        pyplot.show()

def evaluate():
    mysql = pymysql.connect("localhost", "root", "mysqldatabase", "corpus", charset='utf8')
    cursor = mysql.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT `title`, `content` FROM `news` limit 10")
    data = [c["title"] + c["content"] for c in cursor.fetchall()]