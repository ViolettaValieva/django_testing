from http import HTTPStatus

from .base_test import BaseTestCase
from .constants import (DELETE_URL, DETAIL_URL, EDIT_URL, HOME_URL,
                        LOGIN_URL, LOGOUT_URL, SIGNUP_URL)


class TestNotesRoutes(BaseTestCase):

    def test_pages_availability_for_author(self):
        """Тест доступности страниц для автора."""
        for url in self.urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Тест доступности страниц для аутентифицированного пользователя."""
        restricted = (DETAIL_URL, DELETE_URL, EDIT_URL)
        for url in self.urls:
            with self.subTest(url=url):
                response = self.not_author_client.get(url)
                if url in restricted:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_anonymous_user(self):
        """Тест доступности страниц для анонимного пользователя."""
        accessible_pages = (HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL)
        for url in self.urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                if url in accessible_pages:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    redirect_url = f"{LOGIN_URL}?next={url}"
                    self.assertRedirects(response, redirect_url,
                                         fetch_redirect_response=False)
