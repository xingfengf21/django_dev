# import requests
#
# url = "http://127.0.0.1:8000/articles/"
# headers = {'Authorization': 'token d45414b7478d8720ed72ec63437adf18d187488f'}
#
# r = requests.get(url, headers=headers)
#
# print r.status_code
# print r.content
from django.test import TestCase,Client
from rest_framework.test import APITestCase,APIClient

client = APIClient()
print client.login(username='admin', password='admin123')


