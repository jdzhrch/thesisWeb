from django.db import models


# 事件，与report同义，一个事件在数据库中只会存有最新的report
class Event(models.Model):
    eventName = models.CharField(max_length=200)
    reportTime = models.DateField('time when report is generated', auto_now_add=True)
    # 报告版本，会更新，之所以不用reportDate代替reportVer，原因是integer比date的查询效率一定要高，存储也占得少
    reportVer = models.IntegerField(default=1)
    categoryNum = models.IntegerField(default=0)
    searchNum = models.IntegerField(default=0)

    class Meta:
        ordering = ['-searchNum']


# 用户查询事件的历史
class UserHistory(models.Model):
    eventId = models.ForeignKey(Event, on_delete=models.CASCADE)
    openid = models.CharField(max_length=200, default="000")


# 一个categoryId只会用于一个event
class Category(models.Model):
    eventId = models.ForeignKey(Event, on_delete=models.CASCADE)
    featureList = models.CharField(max_length=200)
    reportVer = models.IntegerField(default=1)
    articleNum = models.IntegerField(default=0)


#
class Article(models.Model):
    categoryId = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    content = models.TextField(max_length=40000)
    pv = models.IntegerField(default=0)
