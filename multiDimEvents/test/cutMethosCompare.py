import jieba
import thulac

str = "巴尔的摩枪击案"
thu1 = thulac.thulac()  #默认模式
text = thu1.cut(str, text=True)  #进行一句话分词
seglist = jieba.cut(str)
words = " ".join(seglist)
print(words)
print(text)