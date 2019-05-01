from functools import reduce

from django.http import HttpResponse
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from multiDimEvents import cluster, crawler
from multiDimEvents.models import Event, UserHistory, Category, Article, HotNews
from multiDimEvents.serializers import EventSerializer, CategorySerializer, ArticleSerializer
import operator
from django.db.models import Q


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def processEvent(request):
    """
    获得热点新闻，或创建一个新的 event。
    """
    if request.method == 'GET':
        '''events = Event.objects.all()[0:10]
        serializer = EventSerializer(events, many=True)'''
        # 爬取热点事件，聚类并存入数据库
        # todo 这里应该每天定时处理
        '''HotNews.objects.all().delete()# 清空hotnews
        eventnames = crawler.crawlHotNews()
        print(eventnames)
        for eventname in eventnames:
            cluster.cluster(eventname,True)'''

        hotNews = HotNews.objects.all()
        hotNewsEventIds = list(hotNews.values('eventId'))
        queryOneFit = reduce(operator.or_, (Q(id__contains=hotNewsEventId['eventId']) for hotNewsEventId in hotNewsEventIds))
        eventsOneFit = Event.objects.filter(queryOneFit)
        serializer = EventSerializer(eventsOneFit, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        eventname = request.data["eventname"]
        print(eventname)
        # todo 根据eventname做聚类处理
        # 聚类
        cluster.cluster(eventname,False)
        eventdata = {}
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
        searchkeywords = searchkeyword.split("+")
        print(searchkeywords)
        # 所有关键词都要匹配到,只取出前10条
        queryAllFit = reduce(operator.and_, (Q(eventName__contains=searchkeyword) for searchkeyword in searchkeywords))
        eventsAllFit = Event.objects.filter(queryAllFit)
        # 只要有一个关键词匹配到,只取出前10条
        queryOneFit = reduce(operator.or_, (Q(eventName__contains=searchkeyword) for searchkeyword in searchkeywords))
        eventsOneFit = Event.objects.filter(queryOneFit)
        serializer = EventSerializer(eventsAllFit|eventsOneFit, many=True)
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
        event.searchNum = event.searchNum + 1       # 搜索数加一
        event.save()
        uh.save()
        return Response(status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def getCategory(request):
    """
    根据eventid
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
    根据eventid
    """
    if request.method == 'GET':
        categoryid = request.query_params.dict()['categoryid']
        categories = Article.objects.filter(categoryId=categoryid)
        serializer = ArticleSerializer(categories, many=True)
        return Response(serializer.data)
