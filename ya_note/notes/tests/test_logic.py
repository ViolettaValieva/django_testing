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

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Боб Джек')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.user = User.objects.create(username='Чужак')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.success_url = reverse('notes:success')
        cls.add_url = reverse('notes:add')
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.form_data = {'title': cls.NEW_NOTE_TITLE,
                         'text': cls.NEW_NOTE_TEXT}

    def test_user_can_create_note(self):
        initial_notes_count = Note.objects.count()
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(initial_notes_count + 1, Note.objects.count())
        self.assertTrue(Note.objects.filter(
            title=self.NEW_NOTE_TITLE, text=self.NEW_NOTE_TEXT
        ).exists())

    def test_anonymous_user_cant_create_note(self):
        initial_notes_count = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(initial_notes_count, Note.objects.count())

    def test_author_can_delete_note(self):
        initial_notes_count = Note.objects.count()
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(initial_notes_count - 1, Note.objects.count())

    def test_other_user_cant_delete_note(self):
        initial_notes_count = Note.objects.count()
        response = self.user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(initial_notes_count, Note.objects.count())

    def test_author_can_edit_note(self):
        response = self.auth_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_not_unique_slug(self):
        initial_notes_count = Note.objects.count()
        response = self.auth_client.post(self.add_url, data={
            'title': self.NEW_NOTE_TITLE,
            'text': self.NEW_NOTE_TEXT,
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
        initial_notes_count = Note.objects.count()
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(initial_notes_count + 1, Note.objects.count())
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
