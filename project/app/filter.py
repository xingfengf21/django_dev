#coding=utf-8

import django_filters
from app.models import Article,ArticleEditRecord
from app import models
from taggit.models import Tag
from django.db.models.aggregates import Count

class ArticleFilter(django_filters.rest_framework.FilterSet):
    title = django_filters.CharFilter(name='title', lookup_expr='icontains')
    tags = django_filters.ModelMultipleChoiceFilter(
        name="tag__name",
        #queryset = Tag.objects.filter(),
        queryset = Tag.objects.all().annotate(count=Count("article")).filter(count__gt=0).filter(),
        to_field_name='name',
        # lookup_expr='in',
        label=u'标签分类'
    )
    class Meta:
        model = Article
        fields = ['user', 'post_status',"title","tags"]


class ArticleRecordFilter(django_filters.rest_framework.FilterSet):
    #title = django_filters.CharFilter(name='title', lookup_expr='icontains')
    # article_id = django_filters.CharFilter(article_id="article_id")

    class Meta:
        model = ArticleEditRecord
        fields = ['id','edid_user','article']

class TagFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = ArticleEditRecord
        fields = ['id','edid_user','article']

