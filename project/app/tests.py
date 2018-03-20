# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase,Client
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

# Create your tests here.
from rest_framework.test import APIClient
from django.core.urlresolvers import reverse
from rest_framework import status
from django.contrib.auth import authenticate

from app import  models

class ArticleApiTests(APITestCase):

    def authentication(self):
        self.user1 = dict(username='admin', email='', password='admin123')
        User.objects.create_superuser(**self.user1)
        self.client.login(**self.user1)

    def new_add_one_article(self,data):
        self.authentication()
        path = "http://localhost:8000/articles/"
        resp = self.client.post(path=path, data=data,format='json')

    def edit_article(self,article_id,data):
        path = "http://localhost:8000/article/%s/" % article_id
        resp = self.client.put(path=path, data=data, format='json')
        self.assertEqual(resp.status_code, 200)
        return resp

    def setUp(self):
        # self.user1 = dict(username='admin', email='', password='admin123')
        # User.objects.create_superuser(**self.user1)
        # self.client.login(**self.user1)
        pass
        # client = APIClient()
        # client.login(username='admin', password='admin123')

    def test_get_article_lists(self):
        self.authentication()
        data = {
            "title": "test",
            "body_text": "for test",
            "post_status": "post"
        }
        path = "http://localhost:8000/articles/"
        resp = self.client.post(path=path, data=data,format='json')

        resp = self.client.get(path=path,format='json')
        # print "response xxxx",resp.status_code,resp.data,len(resp.data)
        self.assertEqual(resp.status_code,200)
        self.assertEqual(len(resp.data),1)

        data = {
            "title": "test2",
            "body_text": "for test2",
            "post_status": "post"
        }
        resp = self.client.post(path=path, data=data, format='json')
        self.assertEqual(resp.data["title"], "test2")
        self.assertEqual(resp.data["body_text"], "for test2")
        resp = self.client.get(path=path, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

    def test_create_new_article(self):
        self.authentication()
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
        self.authentication()
        path = "http://localhost:8000/users/"
        resp = self.client.get(path=path, format='json')
        self.assertEqual(resp.status_code,200)
        self.assertEqual(resp.data[0]["username"],"admin")


    def test_user_view(self):
        self.authentication()
        path = "http://localhost:8000/user/1/"
        resp = self.client.get(path=path, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["username"],"admin")

    def test_when_not_login_article_lists_should_return_401(self):
        path = "http://localhost:8000/articles/"
        data = {
            "title": "my_like_test",
            "body_text": "for test",
            "post_status": "post"
        }
        resp = self.client.post(path=path, data=data, format='json')
        self.assertEqual(resp.status_code,401)

    def test_when_login_article_like_article_like_count_should_add_1(self):
        self.authentication()
        data = {
            "title": "my_like_test",
            "body_text": "for test",
            "post_status": "post"
        }
        path = "http://localhost:8000/articles/"
        resp = self.client.post(path=path, data=data,format='json')

        path = "http://localhost:8000/likes/"
        article= models.Article.objects.filter(title="my_like_test").first()
        self.assertEqual(article.like_count,0)
        data = {
            "article": article.id
         }
        resp = self.client.post(path=path, data=data, format='json')
        self.assertEqual(resp.status_code, 201)
        article = models.Article.objects.filter(title="my_like_test").first()
        self.assertEqual(article.like_count, 1)
        #再次点赞不影响文章的like_count
        resp = self.client.post(path=path, data=data, format='json')
        article = models.Article.objects.filter(title="my_like_test").first()
        self.assertEqual(article.like_count, 1)

    def test_tag(self):
        tag_path = "http://localhost:8000/tags/"
        resp = self.client.get(path=tag_path,format='json')
        self.assertEqual(resp.status_code,401)
        self.authentication()
        resp = self.client.get(path=tag_path,format='json')
        self.assertEqual(resp.data,[])
        data = {
            "title": "my_like_test",
            "body_text": "for test",
            "post_status": "post"
        }
        article_path = "http://localhost:8000/articles/"
        resp = self.client.post(path=article_path, data=data,format='json')
        resp = self.client.get(path=tag_path,format='json')
        self.assertNotEqual(resp.data,[])

    def test_when_new_one_article_tags_should_add(self):
        self.authentication()
        data = {
            "title": "tags test",
            "body_text": "tag test",
            "post_status": "post"
        }
        article_path = "http://localhost:8000/articles/"
        resp = self.client.post(path=article_path, data=data,format='json')
        article = models.Article.objects.filter(title="tags test").first()
        self.assertIsNotNone(article)
        self.assertIsNotNone(article.tags.all())

    def test_when_edit_one_article_tags_should_add(self):
        data = {
            "title": "title",
            "body_text": "for test",
            "post_status": "post"
        }
        self.new_add_one_article(data=data)
        article = models.Article.objects.filter(title="title").first()
        self.assertIsNotNone(article)
        article_id = article.id
        tags_count_before = len(article.tags.all())
        path = "http://localhost:8000/article/%s/" % article_id
        data = {
            "id": article_id,
            "title": "title_edid",
            "body_text": "我们需要先认识一些重要的基本元素z",
            "post_status": "post"
        }
        resp = self.client.put(path=path,data=data,format='json')
        self.assertEqual(resp.status_code,200)
        article = models.Article.objects.filter(title="title_edid").first()
        self.assertIsNotNone(article)
        tags_count_after = len(article.tags.all())
        self.assertNotEqual(tags_count_before,tags_count_after)


    def test_when_article_is_post_mult_authors_should_can_edit(self):
        data = {
            "title": "title",
            "body_text": "for test",
            "post_status": "post"
        }
        self.new_add_one_article(data=data)

        self.client.logout()

        self.user1 = dict(username='admin2', email='', password='admin123')
        User.objects.create_superuser(**self.user1)
        self.client.login(**self.user1)

    def test_when_article_is_not_post_ower_author_should_can_view_and_edit(self):
        data = {
            "title": "title",
            "body_text": "for test",
            "post_status": "unpost"
        }
        self.new_add_one_article(data=data)

        self.client.logout()

        self.user1 = dict(username='admin2', email='', password='admin123')
        User.objects.create_superuser(**self.user1)
        self.client.login(**self.user1)

        article = models.Article.objects.filter(title="title").first()
        self.assertIsNone(article)

    def test_when_one_author_edit_same_article_should_record_edit_history(self):
        data = {
            "title": "title",
            "body_text": "for test",
            "post_status": "post"
        }
        self.new_add_one_article(data=data)

        article = models.Article.objects.filter(title="title").first()
        self.assertIsNotNone(article)
        article_id = article.id
        data = {
            "id": article_id,
            "title": "title_edid",
            "body_text": "我们需要先认识一些重要的基本元素z",
            "post_status": "post"
        }

        self.edit_article(article_id=article_id,data=data)

        data = {
            "id": article_id,
            "title": "title_edid_two",
            "body_text": "我们需要先认识一些重要的基本元素z2",
            "post_status": "post"
        }

        self.edit_article(article_id=article_id, data=data)

        record_count = models.ArticleEditRecord.objects.filter(
            article_id=article_id,
            edid_user=1
        ).all()

        self.assertEqual(len(record_count),2)

    def test_when_mult_author_edit_same_article_should_record_edit_history(self):
        data = {
            "title": "title",
            "body_text": "for test",
            "post_status": "post"
        }
        self.new_add_one_article(data=data)

        article = models.Article.objects.filter(title="title").first()
        self.assertIsNotNone(article)
        article_id = article.id
        data = {
            "id": article_id,
            "title": "title_edid",
            "body_text": "我们需要先认识一些重要的基本元素z",
            "post_status": "post"
        }

        self.edit_article(article_id=article_id,data=data)

        self.client.logout()

        self.user1 = dict(username='admin2', email='', password='admin123')
        User.objects.create_superuser(**self.user1)
        self.client.login(**self.user1)

        data = {
            "id": article_id,
            "title": "title_edid_two",
            "body_text": "我们需要先认识一些重要的基本元素z2",
            "post_status": "post"
        }

        self.edit_article(article_id=article_id, data=data)

        admin_record = models.ArticleEditRecord.objects.filter(
            article_id=article_id,
            edid_user=1
        ).all()

        admin2_record = models.ArticleEditRecord.objects.filter(
            article_id=article_id,
            edid_user=2
        ).all()

        self.assertEqual(len(admin_record),1)
        self.assertEqual(len(admin2_record), 1)

    def test_article_records_when_filer_by_edit_user_or_article_should_be_display(self):
        data = {
            "title": "title",
            "body_text": "for test",
            "post_status": "post"
        }
        self.new_add_one_article(data=data)

        article = models.Article.objects.filter(title="title").first()
        self.assertIsNotNone(article)
        article_id = article.id
        data = {
            "id": article_id,
            "title": "title_edid",
            "body_text": "我们需要先认识一些重要的基本元素z",
            "post_status": "post"
        }

        self.edit_article(article_id=article_id,data=data)

        path = "http://localhost:8000/article_records/?edid_user=%s" % 1

        resp = self.client.get(path=path)
        self.assertEqual(resp.status_code,200)
        self.assertNotEqual(resp.data,[])

        path = "http://localhost:8000/article_records/?article=%s" % 1

        resp = self.client.get(path=path)
        self.assertEqual(resp.status_code,200)
        self.assertNotEqual(resp.data,[])


    def test_tags_when_one_article_is_create_or_update_should_be_display(self):
        data = {
            "title": "title",
            "body_text": "for test",
            "post_status": "post"
        }
        self.new_add_one_article(data=data)

        path = "http://localhost:8000/tags/"
        resp = self.client.get(path=path,format="json")
        self.assertNotEqual(resp.data,[])
        self.assertEqual(resp.status_code,200)

        article = models.Article.objects.filter(title="title").first()
        self.assertIsNotNone(article)
        article_id = article.id
        data = {
            "id": article_id,
            "title": "title_edid",
            "body_text": "我们需要先认识一些重要的基本元素z",
            "post_status": "post"
        }

        self.edit_article(article_id=article_id,data=data)
        self.assertNotEqual(resp.data,[])
        self.assertEqual(resp.status_code,200)

    def test_when_input_one_article_record_should_rollback(self):
        data = {
            "title": "title",
            "body_text": "for test",
            "post_status": "post"
        }
        self.new_add_one_article(data=data)
        article = models.Article.objects.filter(title="title").first()
        self.assertIsNotNone(article)
        article_id = article.id
        data = {
            "id": article_id,
            "title": "title_edid",
            "body_text": "我们需要先认识一些重要的基本元素z",
            "post_status": "post"
        }

        self.edit_article(article_id=article_id,data=data)
        article_record = models.ArticleEditRecord.objects.get(pk=1)
        record_id  = article_record.id
        data = {
            "article_id":article_id,
            "record_id":article_record.id
        }
        path = "http://localhost:8000/article_rollback/"

        resp = self.client.post(path=path,data=data,format="json")

        self.assertEqual(resp.status_code,201)

        article = models.Article.objects.get(pk=article_id)
        self.assertEqual(article.title,"title")
        self.assertEqual(article.body_text, "for test")
