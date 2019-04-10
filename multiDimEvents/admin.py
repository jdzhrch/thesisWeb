from django.contrib import admin

from .models import Event, Category, Article, UserHistory

admin.site.register(Event)
admin.site.register(UserHistory)
admin.site.register(Article)
admin.site.register(Category)