# -*- coding: utf-8 -*-
from rest_framework import permissions


class IsArticleOwner(permissions.BasePermission):

    message = u'非文章所有者'

    def has_object_permission(self, request, view, obj):
        #obj为Article对象
        print "request.user",request.user
        return obj.user == request.user

class IsArticlePost(permissions.BasePermission):
    message = u'文章不是发布状态'
    def has_object_permission(self, request, view, obj):
        #obj为Article对象
        if obj.user == request.user:
            return True
        return  obj.post_status == "post"
