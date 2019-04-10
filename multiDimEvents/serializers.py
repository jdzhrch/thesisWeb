from rest_framework import serializers

from multiDimEvents.models import Event, UserHistory, Category, Article


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'eventName', 'reportTime', 'reportVer', 'categoryNum')


class UserHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'eventId', 'openid')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'eventId', 'featureList', 'reportVer', 'articleNum')


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'categoryId', 'title', 'url', 'content', 'pv')
