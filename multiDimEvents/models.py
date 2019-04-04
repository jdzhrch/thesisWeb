from django.db import models


# 事件，与report同义，一个事件在数据库中只会存有最新的report
class Event(models.Model):
    eventName = models.CharField(max_length=200)
    reportDate = models.DateTimeField('date when report is generated')


# 用户查询事件的历史
class UserHistory(models.Model):
    eventId = models.ForeignKey(Event, on_delete=models.CASCADE)
    openid = models.IntegerField(default=0)


# 一个categoryId只会用于一个event
class Category(models.Model):
    eventId = models.ForeignKey(Event, on_delete=models.CASCADE)
    featureList = models.CharField(max_length=200)


#
class Article(models.Model):
    categoryId = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    content = models.TextField(max_length=40000)
