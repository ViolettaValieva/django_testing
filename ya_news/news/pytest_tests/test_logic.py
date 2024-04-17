from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_user_can_create_comment(author_client, author, news,
                                 detail_url, form_data):
    """Тест возможности авторизованного пользователя отправлять комментарий."""
    initial_comments_count = Comment.objects.count()
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == initial_comments_count + 1
    comment = Comment.objects.last()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_anonymous_user_cant_create_comment(client, detail_url, form_data):
    """Тест невозможности анонимного пользователя отправлять комментарий."""
    initial_comments_count = Comment.objects.count()
    client.post(detail_url, data=form_data)
    assert Comment.objects.count() == initial_comments_count


def test_user_cant_use_bad_words(author_client, detail_url, news, form_data):
    """
    Тест неопубликования и возвращения ошибки комментария,
    содержащего запрещённые слова.
    """
    initial_comments_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == initial_comments_count


def test_author_can_delete_comment(author_client, comment,
                                   detail_url):
    """
    Тест возможности авторизованного пользователя
    удалять свои комментарии.
    """
    url = reverse('news:delete', args=(comment.id, ))
    initial_comments_count = Comment.objects.count()
    response = author_client.delete(url)
    assertRedirects(response, f'{detail_url}#comments')
    assert initial_comments_count - 1 == Comment.objects.count()


def test_user_cant_delete_comment_of_another_user(reader_client,
                                                  comment):
    """
    Тест невозможности авторизованного пользователя
    удалять чужие комментарии.
    """
    initial_comments_count = Comment.objects.count()
    url = reverse('news:delete', args=(comment.id, ))
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_comments_count


def test_author_can_edit_comment(author_client, author, comment, detail_url,
                                 form_data, news):
    """
    Тест возможности авторизованного пользователя
    редактировать свои комментарии.
    """
    url = reverse('news:edit', args=(comment.id, ))
    initial_comment_count = Comment.objects.count()
    response = author_client.post(url, form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == initial_comment_count
    edited_comment = Comment.objects.get(id=comment.id)
    assert edited_comment.text == form_data['text']
    assert edited_comment.news == news
    assert edited_comment.author == author


def test_user_cant_edit_comment_of_another_user(comment, reader_client,
                                                form_data):
    """
    Тест невозможности авторизованного пользователя
    редактировать чужие комментарии.
    """
    url = reverse('news:edit', args=(comment.id,))
    initial_comment_count = Comment.objects.count()
    response = reader_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_comment_count
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author
