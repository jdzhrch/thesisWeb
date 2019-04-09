from django.http import HttpResponse
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from multiDimEvents.models import Event, UserHistory, Category, Article
from multiDimEvents.serializers import EventSerializer, CategorySerializer, ArticleSerializer


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def addEvent(request):
    """
    列出所有的event，或创建一个新的 event。
    """
    if request.method == 'GET':
        eventid = request.query_params.dict()['eventid']
        events = Event.objects.filter(id=eventid)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        eventname = request.data["eventName"]
        # todo 根据eventname做聚类处理
        eventdata = {}
        serializer = EventSerializer(data=eventdata)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def getHistory(request):
    """
    根据openid找events
    """
    if request.method == 'GET':
        openid = request.query_params.dict()['openid']
        histories = UserHistory.objects.filter(openid=openid)
        queryresults = list(histories.values('eventId')) # [{"eventId':1},]
        eventeds = [i['eventId'] for i in queryresults]
        print(eventeds)

        queryset_result = Event.objects.filter(id = eventeds[0])
        for i in range(1,len(eventeds)):
            queryset_tmp = Event.objects.filter(id = eventeds[i])
            queryset_result = queryset_result|queryset_tmp
        serializer = EventSerializer(queryset_result, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        eventid = request.data["eventid"]
        openid = request.data["openid"]
        event = Event.objects.get(id = eventid)
        uh = UserHistory(eventId=event,openid=openid)
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