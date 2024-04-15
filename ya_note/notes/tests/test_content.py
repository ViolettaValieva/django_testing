from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create(username='Боб')
        cls.user_2 = User.objects.create(username='Джек')
        cls.note_1 = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.user_1
        )

    def test_note_in_list_for_author(self):
        self.client.force_login(self.user_1)
        response = self.client.get(reverse('notes:list'))
        assert self.note_1 in response.context['object_list']

    def test_note_not_in_list_for_another_user(self):
        self.client.force_login(self.user_2)
        response = self.client.get(reverse('notes:list'))
        assert self.note_1 not in response.context['object_list']

    def test_pages_contains_form(self):
        self.client.force_login(self.user_1)
        urls = (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note_1.slug,)),
        )
        for url in urls:
            with self.subTest(url=url):
                responce = self.client.get(url)
                self.assertIn('form', responce.context)
                self.assertIsInstance(responce.context['form'], NoteForm)
