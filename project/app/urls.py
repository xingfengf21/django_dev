# -*- coding: utf-8 -*-
from django.conf.urls import url
from app import views
#return json/html
#from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^login/$', views.UserLoginView.as_view(), name=u'登录'),
    url(r'^users/$', views.UserListView.as_view(), name=u'用户列表和创建'),
    url(r'^user/(?P<pk>[0-9]+)/$',views.UserView.as_view(), name=u'用户查看和修改'),
    url(r'^articles/$', views.ArticleListView.as_view(), name=u'文件列表和创建'),
    url(r'^article/(?P<pk>[0-9]+)/$',
        views.ArticleView.as_view(),
        name=u'文章的查|删|改'),
    url(r'^likes/$', views.UserLikeView.as_view(), name=u'点赞创建'),

    #add
    url(r'^register/$', views.UserRegisterAPIView.as_view(), name=u'用户创建'),
    url(r'^article_records/(?P<pk>[0-9]+)/$',
        views.ArticleEditRecordView.as_view(),
        name=u'文章编辑记录的查|删|改'),
    url(r'^article_records/$', views.ArticleEditRecordListView.as_view(), name=u'文件编辑记录'),
    url(r'^tags/$', views.TagListView.as_view(), name=u'tag列表'),
    url(r'^article_rollback/$', views.ArticleRollbackView.as_view(), name=u'文件回退'),
    url(r'^article_record_diff/$', views.ArticleRecordDiffView.as_view(), name=u'文章记录差异'),
    url(r'^$', views.api_root),
    url(r'^unlikes/$', views.UserUnLikeView.as_view(), name=u'点赞取消'),
]

#urlpatterns = format_suffix_patterns(urlpatterns)