# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
import django.utils.timezone as timezone

class Article(models.Model):
    STATUS_CHOICES =(
        ("post","已发布"),
        ("unport","未发布"),
    )
    user = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    body_text = models.TextField()
    like_count = models.IntegerField(default=0)
    #new add
    post_status = models.CharField("发布状态",choices=STATUS_CHOICES,max_length=40)
    tags = TaggableManager()
    #online = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

class Tag(models.Model):
    #id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(max_length=255)
    articles = models.ManyToManyField(Article)
    # count = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

class Like(models.Model):
    user = models.ForeignKey(User)
    article = models.ForeignKey(Article)

class ArticleEditRecord(models.Model):
    article = models.ForeignKey(Article)
    edid_user = models.ForeignKey(User)
    body_before_edit = models.TextField()
    body_after_edit = models.TextField()
    title_before_edit = models.CharField(max_length=255)
    title_after_edit = models.CharField(max_length=255)
    update_time = models.DateTimeField('update_time',default=timezone.now)
    tags = TaggableManager()

    def __unicode__(self):
        return self.title_before_edit

class Host(models.Model):
    hostname = models.CharField(max_length=32)
    port = models.CharField(max_length=32)

class HostAdmin(models.Model):
    username = models.CharField(max_length=32)
    email = models.CharField(max_length=32)
    host = models.ManyToManyField(Host)


class Publisher(models.Model):
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=60)
    state_province = models.CharField(max_length=30)
    country = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Author(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    email = models.EmailField()

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

class Book(models.Model):
    #id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher)

    def __unicode__(self):
        return self.title