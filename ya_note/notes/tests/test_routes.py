from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс тестов"""

    SLUG = "slug"

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Джон Автор')
        cls.not_author = User.objects.create(username='Джон Авторизованный')
        cls.author_client = Client()
        cls.not_author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug=cls.SLUG
        )
        cls.urls = {
            'home': reverse('notes:home'),
            'list': reverse('notes:list'),
            'add': reverse('notes:add'),
            'success': reverse('notes:success'),
            'detail': reverse('notes:detail', args=(cls.SLUG,)),
            'edit': reverse('notes:edit', args=(cls.SLUG,)),
            'delete': reverse('notes:delete', args=(cls.SLUG,)),
            'login': reverse('users:login'),
            'logout': reverse('users:logout'),
            'signup': reverse('users:signup'),
        }

    def check_availability(self, client, status_code_dict):
        """Универсальная функция для проверки доступа к страницам."""
        for name, url in self.urls.items():
            expected_status = status_code_dict.get(name, HTTPStatus.OK)
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)


class TestNotesRoutes(BaseTestCase):

    def test_pages_availability_for_author(self):
        """Тест доступности страниц для автора."""
        self.check_availability(self.author_client, {})

    def test_pages_availability_for_auth_user(self):
        """
        Тест доступности страниц для
        аутентифицированного пользователя, не автора.
        """
        restricted = {'detail': HTTPStatus.NOT_FOUND,
                      'edit': HTTPStatus.NOT_FOUND,
                      'delete': HTTPStatus.NOT_FOUND}
        self.check_availability(self.not_author_client, restricted)

    def test_pages_availability_for_anonymous_user(self):
        """Тест доступности страниц для анонимного пользователя."""
        accessible_pages = ('home', 'login', 'logout', 'signup')
        restricted_pages = ('list', 'add', 'success', 'detail',
                            'edit', 'delete')
        login_url = self.urls['login']
        for name in accessible_pages:
            url = self.urls[name]
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        for name in restricted_pages:
            url = self.urls[name]
            with self.subTest(url=url):
                response = self.client.get(url)
                redirect_url = f"{login_url}?next={url}"
                self.assertRedirects(response, redirect_url,
                                     fetch_redirect_response=False)
