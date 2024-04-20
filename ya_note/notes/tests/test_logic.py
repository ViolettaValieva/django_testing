from http import HTTPStatus
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .base_test import BaseTestCase
from .constants import ADD_URL, SUCCESS_URL, DELETE_URL, EDIT_URL


class TestRoutes(BaseTestCase):

    def test_user_can_create_note(self):
        """Тест возможности залогиненного пользователя создавать заметку."""
        Note.objects.all().delete()
        response = self.author_client.post(ADD_URL,
                                           data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL,
                             fetch_redirect_response=False)
        self.assertEqual(Note.objects.count(), 1)
        created_note = Note.objects.get()
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.author, self.author)
        self.assertEqual(created_note.slug, self.form_data['slug'])

    def test_anonymous_user_cant_create_note(self):
        """Тест невозможности анонимного пользователя создавать заметку."""
        initial_notes_count = Note.objects.count()
        self.client.post(ADD_URL, data=self.form_data)
        self.assertEqual(initial_notes_count, Note.objects.count())

    def test_author_can_delete_note(self):
        """Тест возможности пользователя удалять свою заметку."""
        initial_notes_count = Note.objects.count()
        response = self.author_client.delete(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(initial_notes_count - 1, Note.objects.count())

    def test_other_user_cant_delete_note(self):
        """Тест невозможности пользователя удалять чужую заметку."""
        initial_notes_count = Note.objects.count()
        response = self.not_author_client.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(initial_notes_count, Note.objects.count())

    def test_author_can_edit_note(self):
        """Тест возможности пользователя редактировать свою заметку"""
        initial_notes_count = Note.objects.count()
        response = self.author_client.post(EDIT_URL, self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(initial_notes_count, Note.objects.count())
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.note.author)

    def test_user_cant_edit_comment_of_another_user(self):
        """Тест невозможности пользователя редактировать чужую заметку."""
        initial_notes_count = Note.objects.count()
        response = self.not_author_client.post(EDIT_URL, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(initial_notes_count, Note.objects.count())
        new_note = Note.objects.get()
        self.assertNotEqual(new_note.title, self.form_data['title'])
        self.assertNotEqual(new_note.text, self.form_data['text'])
        self.assertNotEqual(new_note.slug, self.form_data['slug'])
        self.assertNotEqual(new_note.author, self.not_author)

    def test_not_unique_slug(self):
        """Тест невозможности создания двух заметок с одинаковым slug."""
        initial_notes_count = Note.objects.count()
        response = self.author_client.post(ADD_URL, data={
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
        """Тест автоматического формирования slug, если он не заполнен."""
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))
        self.assertEqual(new_note.author, self.author)
