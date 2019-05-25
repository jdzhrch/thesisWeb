from functools import reduce

from django.http import HttpResponse
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from multiDimEvents.utils import cluster, cronjob
from multiDimEvents.models import Event, UserHistory, Category, Article, HotNews
from multiDimEvents.serializers import EventSerializer, CategorySerializer, ArticleSerializer
import operator
from django.db.models import Q

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

'''定时任务，定时存入热点新闻'''
try:
    # 实例化调度器
    scheduler = BackgroundScheduler()
    # 调度器使用DjangoJobStore()
    scheduler.add_jobstore(DjangoJobStore(), "default")


    # 'cron'方式循环，每天9:30:10执行,id为工作ID作为标记
    # ('scheduler',"interval", seconds=1)  #用interval方式循环，每一秒执行一次
    @register_job(scheduler, 'cron', hour='15', minute='52', second='30', id='task_time')
    def test_job():
        print("开始定时任务")
        cronjob.getHotNews()
        # 监控任务


    register_events(scheduler)
    # 调度器开始
    scheduler.start()
except Exception as e:
    print(e)
    # 报错则调度器停止执行
    scheduler.shutdown()


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def processEvent(request):
    """
    获得热点新闻，或创建一个新的 event。
    """
    if request.method == 'GET':
        hotNews = HotNews.objects.all()
        hotNewsEventIds = list(hotNews.values('eventId'))
        if len(hotNewsEventIds) == 0:
            none_result = Event.objects.filter(id=-1)
            serializer = EventSerializer(none_result, many=True)
            return Response(serializer.data)
        else:
            queryOneFit = reduce(operator.or_,
                                 (Q(id__contains=hotNewsEventId['eventId']) for hotNewsEventId in hotNewsEventIds))
            eventsOneFit = Event.objects.filter(queryOneFit)
            serializer = EventSerializer(eventsOneFit, many=True)
            return Response(serializer.data)
    elif request.method == 'POST':
        eventname = request.data["eventname"]
        print(eventname)
        # 聚类
        cluster.cluster(eventname, False, "ap")
        return Response(status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def searchEvent(request):
    """
    列出所有的event，或创建一个新的 event。
    目前history的模型采用的方式是同一个user搜索同一个event，会有多条记录
    """
    if request.method == 'GET':
        searchkeyword = request.query_params.dict()['searchkeyword']
        searchkeywords = list(filter(None, searchkeyword.split("+")))  # filter函数能去除空字符串
        print(searchkeywords)
        if searchkeywords == []:
            none_result = Event.objects.filter(id=-1)
            serializer = EventSerializer(none_result, many=True)
            return Response(serializer.data)
        else:
            # todo 所有关键词都要匹配到,只取出前10条
            queryAllFit = reduce(operator.and_,
                                 (Q(eventName__contains=searchkeyword) for searchkeyword in searchkeywords))
            eventsAllFit = Event.objects.filter(queryAllFit)  # [:10]
            # 只要有一个关键词匹配到,只取出前10条
            queryOneFit = reduce(operator.or_,
                                 (Q(eventName__contains=searchkeyword) for searchkeyword in searchkeywords))
            eventsOneFit = Event.objects.filter(queryOneFit)  # [:10]
            serializer = EventSerializer(eventsAllFit | eventsOneFit, many=True)
            return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def processHistory(request):
    """
    根据openid找events
    """
    if request.method == 'GET':
        openid = request.query_params.dict()['openid']
        histories = UserHistory.objects.filter(openid=openid)
        queryresults = list(histories.values('eventId'))  # [{"eventId':1},]
        if len(queryresults) == 0:
            none_result = Event.objects.filter(id=-1)
            serializer = EventSerializer(none_result, many=True)
            return Response(serializer.data)
        else:
            queryOneFit = reduce(operator.or_,
                                 (Q(id__contains=queryresult['eventId']) for queryresult in queryresults))
            eventsOneFit = Event.objects.filter(queryOneFit)
            serializer = EventSerializer(eventsOneFit, many=True)
            return Response(serializer.data)

    elif request.method == 'POST':
        print(request.data)
        eventid = request.data["eventid"]
        openid = request.data["openid"]
        event = Event.objects.get(id=eventid)
        uh = UserHistory(eventId=event, openid=openid)
        event.searchNum = event.searchNum + 1  # 搜索数加一
        event.save()
        uh.save()
        return Response(status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def getCategory(request):
    """
    根据eventid找categories
    """
    if request.method == 'GET':
        eventid = request.query_params.dict()['eventid']
        reportver = request.query_params.dict()['reportver']
        categories = Category.objects.filter(eventId=eventid).filter(reportVer=reportver)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def getArticle(request):
    """
    根据categoryid找articles
    """
    if request.method == 'GET':
        categoryid = request.query_params.dict()['categoryid']
        articles = Article.objects.filter(categoryId=categoryid)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)
