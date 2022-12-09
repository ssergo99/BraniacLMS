from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse


class TestMainPage(TestCase):
    def test_page_open(self):
        path = reverse("mainapp:index")
        result = self.client.get(path)
        self.assertEqual(result.status_code, HTTPStatus.OK)
