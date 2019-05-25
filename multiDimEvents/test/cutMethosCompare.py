import jieba

text = '彭博新闻社网站5月22日的文章称，美中贸易争端的影响不再只是局限于这两个国家。'

seg_list = jieba.cut(text, cut_all=True)
print("全模式:\n" + "/ ".join(seg_list))

seg_list = jieba.cut(text, cut_all=False, HMM=False)
print("默认模式:\n" + "/ ".join(seg_list))

seg_list = jieba.cut(text, cut_all=False, HMM=True)
print("默认模式+HMM:\n" + "/ ".join(seg_list))