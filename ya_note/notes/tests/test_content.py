from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст'
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
            'list': reverse('notes:list'),
            'add': reverse('notes:add'),
            'edit': reverse('notes:edit', args=(cls.SLUG,))
        }

    def test_note_in_list_for_author(self):
        """
        Тест передачи отдельной заметки на страницу со списком заметок в
        списке object_list в словаре context
        """
        response = self.author_client.get(self.urls['list'])
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 1)
        note = object_list.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, self.SLUG)

    def test_note_not_in_list_for_another_user(self):
        """
        Тест непопадания в список заметок одного пользователя
        заметок другого пользователя
        """
        response = self.not_author_client.get(self.urls['list'])
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 0)

    def test_pages_contains_form(self):
        """
        Тест передачи формы на страницы создания и
        редактирования заметки.
        """
        pages = ('add', 'edit')
        for name in pages:
            with self.subTest(name=name):
                responce = self.author_client.get(self.urls[name])
                self.assertIn('form', responce.context)
                self.assertIsInstance(responce.context['form'], NoteForm)
