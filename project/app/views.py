# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import permissions, generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from app import serializers, models
from app.permissions import IsArticleOwner,IsArticlePost
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from app.filter import ArticleFilter,ArticleRecordFilter
from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
@api_view(('GET',))
def api_root(request, format=None):
    print "request",request
    return Response({
        u'文件列表和创建': reverse(u'文件列表和创建', request=request, format=format),
        u'文件编辑记录': reverse(u'文件编辑记录', request=request, format=format),
    })


class UserLoginView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny, )
    queryset = models.User.objects.all()
    serializer_class = serializers.UserLoginSerializer

    def post(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # return Response()
        request_data = request.data
        username = request_data.get("username")
        password = request_data.get("password")
        user = models.User.objects.get(username__exact=username)
        if user.password == password:
            serializer = serializers.UserSerializer(user)
            new_data = serializer.data
            # 记忆已登录用户
            request.session['user_id'] = user.id
            request.session.set_expiry(600)
            return Response(new_data, status=HTTP_200_OK)
        return Response('password error', HTTP_400_BAD_REQUEST)


class UserRegisterAPIView(APIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        data = request.data
        username = data.get('username')
        if models.User.objects.filter(username__exact=username):
            return Response("用户名已存在", HTTP_400_BAD_REQUEST)
        serializer = serializers.UserRegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

#继承ListCreateAPIView,包含创建、列表
class UserListView(generics.ListCreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    #仅限管理员可使用此视图
    permission_classes = (IsAdminUser, )

class ArticleRollbackView(generics.ListCreateAPIView):
    queryset = models.Article.objects.all()
    serializer_class = serializers.ArticleSerializer
    #permission_classes = (permissions.IsAuthenticated,)
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        data =  self.request.data
        print "data",data
        article_id = data.get("article_id")
        record_id = data.get("record_id")
        print "article_id", article_id
        print "record_id", record_id
        article = models.Article.objects.filter(pk=article_id).first()
        article_record = models.ArticleEditRecord.objects.filter(pk=record_id).first()
        print "article",article
        print "article_record", article_record
        if not article or not article_record:
            return Response("not found",status=404)
        article.title = article_record.title_before_edit
        article.body_text = article_record.body_before_edit
        article.save()
        return Response("ok", status=status.HTTP_201_CREATED)

class ArticleListView(generics.ListCreateAPIView):
    # articles = models.Article.objects.all()
    # queryset = articles.order_by("-like_count")

    #IsAuthenticated 登陆用户可使用此视图
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,)
    filter_class = ArticleFilter
    #search_fields = ('user','post_status')

    def get_queryset(self):
        user_articles = models.Article.objects.filter(user_id=self.request.user)
        post_articles = models.Article.objects.filter(post_status="post")
        articles = post_articles | user_articles
        for a in articles:
            tags = a.tags.all()
            print "a-tags",tags
            for tag in tags:
                print "one_tag",tag
        queryset = articles.order_by("-like_count")
        print "queryset",queryset
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            #创建的情况
            self.serializer_class = serializers.ArticleSerializer
        else:
            #列表的情况
            print "method",self.request.method
            self.serializer_class = serializers.ArticleListSerializer
        return super(ArticleListView, self).get_serializer_class()

    def perform_create(self, serializer):
        #创建前传入user
        serializer.save(user=self.request.user)

class ArticleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Article.objects.all()
    serializer_class = serializers.ArticleSerializer
    permission_classes = (permissions.IsAuthenticated, IsArticlePost)

    def perform_destroy(self, instance):
        #instance.tag_set.all().delete()
        instance.delete()

class UserLikeView(generics.CreateAPIView):
    serializer_class = serializers.LikeSerializer
    permission_classes = (permissions.IsAuthenticated, )

class UserView(generics.RetrieveUpdateDestroyAPIView):
    #queryset = models.Article.objects.all()
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminUser)

    def get(self, request, *args, **kwargs):
        print "test",request.data
        print "args",kwargs,args
        return self.retrieve(request, *args, **kwargs)


class ArticleEditRecordView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ArticleEditRecord.objects.all()
    serializer_class = serializers.ArticleEditRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

class ArticleEditRecordListView(generics.ListCreateAPIView):
    queryset = models.ArticleEditRecord.objects.all()
    serializer_class = serializers.ArticleEditRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_class = ArticleRecordFilter
    #filter_fields = ('edid_user',"id")

class TagListView(generics.ListCreateAPIView):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagListSerializer
    permission_classes = (permissions.IsAuthenticated,)

class ArticleRecordDiffView(generics.GenericAPIView):
    queryset = models.ArticleEditRecord.objects.all()
    serializer_class = serializers.ArticleRecordDiffSerialier
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = serializers.ArticleRecordDiffSerialier(data=request.data)
        serializer.is_valid()
        return Response(serializer.diff())


class UserUnLikeView(generics.CreateAPIView):
    queryset = models.ArticleEditRecord.objects.all()
    serializer_class = serializers.UnLikeSerializer
    permission_classes = (permissions.IsAuthenticated, )

    # def post(self, request, *args, **kwargs):
    #     print "request",request
    #     serializer = serializers.UnLikeSerializer(data=request.data)
    #     serializer.is_valid()
    #     return Response("ok",status=202)