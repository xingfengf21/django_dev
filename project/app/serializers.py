# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate, login
from django.db.models import F
from rest_framework import serializers
from app.models import Like, Article, User, ArticleEditRecord, Tag
import jieba
import jieba.analyse

from app import signals
from taggit import models as tagggit_models
from django.db.models import Sum


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(label=u'用户名')
    password = serializers.CharField(label=u'密码', min_length=6)

    def validate(self, data):
        user = User.objects.filter(username__iexact=data['username']).first()
        # 检查密码是否相同
        if user and user.check_password(data['password']):
            # 相同就登录
            login(self.context['request'], user)
        else:
            raise serializers.ValidationError(u'登录失败')
        return data


class UserSerializer(serializers.ModelSerializer):
    # password = serializers.SerializerMethodField()
    #
    # def get_password(self,obj):
    #     return "*"*20

    @property
    def data(self):
        data = super(UserSerializer, self).data
        if "password" in data:
            data["password"] = "*"*6
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    class Meta:
        model = User
        # 列表展示的字段、创建时需要的字段
        fields = ('id', 'username', 'password')

    def create(self, validated_data):
        print "validated_data",validated_data
        instance = super(UserSerializer, self).create(validated_data)
        # 密码是通过set_password生成hash，进一步再保存
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class ArticleListSerializer(serializers.ModelSerializer):
    like_users = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source='user.username')
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        print "obj_type", type(obj), obj
        return obj.tags.names()

    def get_like_users(self, obj):
        # obj  为一个文章实例
        data = list(
            Like.objects.filter(article=obj).order_by('-id').values_list(
                'user__username', flat=True))
        return data

    class Meta:
        model = Article
        fields = ("id", "title", "body_text", "like_count",
                  "like_users", "post_status", "user", "tags")


class ArticleSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source='user.username')

    def get_tags(self, obj):
        from taggit import models
        #from django.db.models import Sum
        from django.db.models.aggregates import Count
        tags = models.Tag.objects.all().values("name")
        t = tags.annotate(count=Count("article")).filter(count__gt=0)
        return t

    class Meta:
        model = Article
        fields = ("id", "title", "body_text", "post_status", "tags", "user")

    def create(self, validated_data):
        instance = super(ArticleSerializer,self).create(validated_data)
        print "validated_data:", validated_data
        text = validated_data.get('body_text', instance.body_text)
        tag_names = jieba.analyse.extract_tags(text, topK=3)
        article = Article.objects.filter(pk=instance.id).first()
        for tag_name in tag_names:
            print "___tags__", tag_name
            tag = Tag.objects.filter(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                tag.save()
            tag.articles.add(article)
            tag.save()
            instance.tags.add(tag_name)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        print "validated_data:", validated_data
        text = validated_data.get('body_text', instance.body_text)
        # if text == instance.body_text:
        #     print ("No changes.")
        #     return instance
        tag_names = jieba.analyse.extract_tags(text, topK=3)
        article = Article.objects.filter(pk=instance.id).first()
        instance.tags.clear()
        for tag_name in tag_names:
            print "___tags__", tag_name
            tag = Tag.objects.filter(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                tag.save()
            # else:
            #     if article not in tag.articles.all():
            #         tag.count = tag.count + 1
            tag.articles.add(article)
            tag.save()
            instance.tags.add(tag_name)
        user = self.context["request"].user
        print "user", user
        user_id = user.id
        print "user_id", user_id
        title = validated_data.get('title', instance.title)
        instance.title = title
        title_before_edit = instance.title
        body_before_edit = instance.body_text
        body_text = validated_data.get('body_text', instance.body_text)
        instance.body_text = body_text
        instance.like_count = validated_data.get(
            'like_count', instance.like_count)
        instance.post_status = validated_data.get(
            'post_status', instance.post_status)
        instance.save()
        edid_user = User.objects.get(id=user_id)
        signals.ArticleRecordSignal.send(sender=Article,
                                         instance=instance,
                                         edid_user=edid_user,
                                         body_before_edit=body_before_edit,
                                         body_after_edit=body_text,
                                         title_before_edit=title_before_edit,
                                         title_after_edit=title,
                                         )
        return instance


class LikeSerializer(serializers.ModelSerializer):
    def validate(self, data):
        like = Like.objects.filter(
            article=data["article"],
            user=self.context['request'].user).first()
        if like:
            raise serializers.ValidationError(u'已经点过赞了')
        data['user'] = self.context['request'].user
        return data

    def create(self, validated_data):
        instance = super(LikeSerializer, self).create(validated_data)
        # 防止top脏读、脏写
        instance.article.like_count = F("like_count") + 1
        instance.article.save()
        return instance

    class Meta:
        model = Like
        fields = ('article', )

# add
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')


class ArticleEditRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleEditRecord
        fields = ("id",
                  "article_id",
                  "edid_user",
                  "body_before_edit",
                  "body_after_edit",
                  "title_before_edit",
                  "title_after_edit",
                  "update_time",
                  )


class TagListSerializer(serializers.ModelSerializer):
    #tags = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    def get_count(self, obj):
        print "obj_type", type(obj), obj
        from taggit import models
        from django.db.models import Sum,Count
        #tags = models.Tag.objects.filter(name=obj.name).values("name")
        #t = tags.annotate(count=Count("article")).filter(count__isnull=False)
        tags = models.Tag.objects.filter(name=obj.name).values("name")
        t = tags.annotate(count=Count("article")).filter(count__isnull=False)
        print "__tags", tags
        print "__tt", len(t)
        #print t.first()["count"]
        d = t[0]["count"] if t else 0
        if not d:
            Tag.objects.filter(name=obj.name).delete()
        return d

    class Meta:
        model = Tag
        fields = ("name","count")


class ArticleRecordDiffSerialier(serializers.Serializer):
    record1 = serializers.ChoiceField(choices=ArticleEditRecord.objects.all())
    record2 = serializers.ChoiceField(
        choices=ArticleEditRecord.objects.all(), allow_blank=True)
    # class Meta:
    #     module=ArticleEditRecord

    def diff(self, *args, **kwargs):
        record1 = self.validated_data
        record2 = self.validated_data
        print "validated_data", record1
        record1 = record1["record1"]
        record2 = record2["record2"]
        if record2:
            if record1.title_before_edit == record2.title_before_edit and \
                    record1.body_before_edit == record2.body_before_edit:
                print "r1 and r2 same"
                return True
            return False
        else:
            article = Article.objects.filter(id=record1.article.id).first()
            if article.title == record1.title_before_edit and article.body_text == record1.body_before_edit:
                print "same with article."
                return True
            return False


class UnLikeSerializer(serializers.ModelSerializer):
    def validate(self, data):
        # like = Like.objects.filter(
        #     article=data["article"],
        #     user=self.context['request'].user).first()
        # if like:
        #     raise serializers.ValidationError(u'已经取消点赞了')
        data['user'] = self.context['request'].user
        article = data["article"]
        print "article=",article
        return data

    def create(self, validated_data):
        print "validated_data",validated_data
        data = validated_data
        like_instance = Like.objects.filter(
             article=data["article"],
             user=data["user"]).first()
        print "like_instance",like_instance
        user = validated_data["user"]
        print user,type(user)
        #instance = super(UnLikeSerializer, self).create(validated_data)
        # # 防止top脏读、脏写
        if not like_instance:
            instance = super(UnLikeSerializer, self).create(validated_data)
            return instance
        if like_instance.article.like_count:
            like_instance.article.like_count = F("like_count") - 1
            like_instance.article.save()
        else:
            raise serializers.ValidationError(u'已经取消点赞了')
        return like_instance

    def update(self, instance, validated_data):
        print "validated_data",validated_data

    class Meta:
        model = Like
        fields = ('article', )
