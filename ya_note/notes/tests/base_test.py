from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note
from .constants import (
    ADD_URL,
    DELETE_URL,
    DETAIL_URL,
    EDIT_URL,
    HOME_URL,
    LIST_URL,
    LOGIN_URL,
    LOGOUT_URL, 
    NEW_NOTE_TEXT,
    NEW_NOTE_TITLE,
    NEW_SLUG,
    NOTE_TEXT,
    NOTE_TITLE,
    SIGNUP_URL,
    SLUG,
    SUCCESS_URL,
)


User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс тестов."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Джон Автор')
        cls.not_author = User.objects.create(username='Джон Авторизованный')
        cls.author_client = Client()
        cls.not_author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            author=cls.author,
            slug=SLUG
        )
        cls.urls = (
            HOME_URL,
            LIST_URL,
            ADD_URL,
            SUCCESS_URL,
            DETAIL_URL,
            EDIT_URL,
            DELETE_URL,
            LOGIN_URL,
            LOGOUT_URL,
            SIGNUP_URL
        )
        cls.form_data = {'title': NEW_NOTE_TITLE,
                         'text': NEW_NOTE_TEXT,
                         'slug': NEW_SLUG}
