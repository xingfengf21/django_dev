# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase,Client
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
import requests
# Create your tests here.
from rest_framework.test import APIClient
from django.core.urlresolvers import reverse
from rest_framework import status
from django.contrib.auth import authenticate

class ArticleApiTests(APITestCase):
    def setUp(self):
        self.user1 = dict(username='admin', email='', password='admin123')
        User.objects.create_superuser(**self.user1)
        self.client.login(**self.user1)

        # client = APIClient()
        # client.login(username='admin', password='admin123')

    def test_get_article_lists(self):
        data = {
            "title": "test",
            "body_text": "for test",
            "post_status": "post"
        }
        path = "http://localhost:8000/articles/"
        resp = self.client.post(path=path, data=data,format='json')
        path  = "http://localhost:8000/articles/"
        resp = self.client.get(path=path,format='json')
        #print "response",resp.status_code,resp
        self.assertEqual(resp.status_code,200)

    def test_create_new_article(self):
        data = {
            "title": "test",
            "body_text": "for test",
            "post_status": "post"
        }
        path = "http://localhost:8000/articles/"
        resp = self.client.post(path=path, data=data,format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["body_text"],"for test")
        self.assertEqual(resp.data["post_status"],"post")


    def test_user_lists(self):
        path = "http://localhost:8000/users/"
        resp = self.client.get(path=path, format='json')
        print "user",resp.data
        self.assertEqual(resp.status_code,200)


    def test_user_view(self):
        path = "http://localhost:8000/user/1/"
        resp = self.client.get(path=path, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["username"],"admin")
        #print "user password",resp.data['password']