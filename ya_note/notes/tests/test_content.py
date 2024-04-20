from notes.forms import NoteForm
from .base_test import BaseTestCase
from .constants import ADD_URL, EDIT_URL, LIST_URL


class TestRoutes(BaseTestCase):

    def test_note_in_list_for_author(self):
        """Тест передачи отдельной заметки на страницу со списком заметок."""
        response = self.author_client.get(LIST_URL)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 1)
        note = object_list.get()
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note.slug)

    def test_note_not_in_list_for_another_user(self):
        """Тест непопадания в список заметок других пользователей."""
        response = self.not_author_client.get(LIST_URL)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 0)

    def test_pages_contains_form(self):
        """Тест передачи формы на страницы создания и редактирования."""
        for page in (ADD_URL, EDIT_URL):
            with self.subTest(page=page):
                responce = self.author_client.get(page)
                self.assertIn('form', responce.context)
                self.assertIsInstance(responce.context['form'], NoteForm)
