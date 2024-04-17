from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст'
    NEW_NOTE_TITLE = 'Новый заголовок'
    NEW_NOTE_TEXT = 'Новый текст'
    SLUG = "slug"
    NEW_SLUG = slugify(NEW_NOTE_TITLE)

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Джон Автор')
        cls.not_author = User.objects.create(username='Джон Авторизованный')
        cls.author_client = Client()
        cls.not_author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.SLUG
        )
        cls.form_data = {'title': cls.NEW_NOTE_TITLE,
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': cls.NEW_SLUG}
        cls.urls = {
            'add': reverse('notes:add'),
            'success': reverse('notes:success'),
            'edit': reverse('notes:edit', args=(cls.SLUG,)),
            'delete': reverse('notes:delete', args=(cls.SLUG,)),
        }

    def test_user_can_create_note(self):
        """Тест возможности залогиненного пользователя создавать заметку."""
        Note.objects.all().delete()
        self.assertEqual(Note.objects.count(), 0)
        response = self.author_client.post(self.urls['add'],
                                           data=self.form_data)
        self.assertRedirects(response, self.urls['success'],
                             fetch_redirect_response=False)
        self.assertEqual(Note.objects.count(), 1)
        created_note = Note.objects.get()
        self.assertEqual(created_note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(created_note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(created_note.author, self.author)
        self.assertEqual(created_note.slug, self.NEW_SLUG)

    def test_anonymous_user_cant_create_note(self):
        """Тест невозможности анонимного пользователя создавать заметку."""
        initial_notes_count = Note.objects.count()
        self.client.post(self.urls['add'], data=self.form_data)
        self.assertEqual(initial_notes_count, Note.objects.count())

    def test_author_can_delete_note(self):
        """Тест возможности пользователя удалять свою заметку."""
        initial_notes_count = Note.objects.count()
        response = self.author_client.delete(self.urls['delete'])
        self.assertRedirects(response, self.urls['success'])
        self.assertEqual(initial_notes_count - 1, Note.objects.count())

    def test_other_user_cant_delete_note(self):
        """Тест невозможности пользователя удалять чужую заметку."""
        initial_notes_count = Note.objects.count()
        response = self.not_author_client.delete(self.urls['delete'])
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(initial_notes_count, Note.objects.count())

    def test_author_can_edit_note(self):
        """Тест возможности пользователя редактировать свою заметку"""
        self.assertEqual(Note.objects.count(), 1)
        response = self.author_client.post(self.urls['edit'], self.form_data)
        self.assertRedirects(response, self.urls['success'])
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(new_note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(new_note.slug, self.NEW_SLUG)

    def test_user_cant_edit_comment_of_another_user(self):
        """Тест невозможности пользователя редактировать чужую заметку."""
        self.assertEqual(Note.objects.count(), 1)
        response = self.not_author_client.post(self.urls['edit'],
                                               self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        new_note = Note.objects.get()
        self.assertNotEqual(new_note.title, self.NEW_NOTE_TITLE)
        self.assertNotEqual(new_note.text, self.NEW_NOTE_TEXT)
        self.assertNotEqual(new_note.slug, self.NEW_SLUG)

    def test_not_unique_slug(self):
        """Тест невозможности создания двух заметок с одинаковым slug."""
        initial_notes_count = Note.objects.count()
        response = self.author_client.post(self.urls['add'], data={
            'title': self.form_data['title'],
            'text': self.form_data['text'],
            'slug': self.note.slug
        })
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(initial_notes_count, Note.objects.count())

    def test_empty_slug(self):
        """
        Тест автоматического формирования slug,
        если при создании заметки он не заполнен.
        """
        Note.objects.all().delete()
        self.assertEqual(Note.objects.count(), 0)
        response = self.author_client.post(self.urls['add'], data={
            'title': self.form_data['title'],
            'text': self.form_data['text'],
        })
        self.assertRedirects(response, self.urls['success'])
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
