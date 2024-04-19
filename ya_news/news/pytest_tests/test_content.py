import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_anonymous_client_has_no_form(client, detail_url):
    """Тест недоступности анонимному пользователю формы для отправки"""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(reader_client, detail_url):
    """Тест доступности авторизованному  пользователю формы для отправки"""
    response = reader_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_news_count(client, all_news, home_url):
    """Тест количества новостей на главной странице — не более 10."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, all_news, home_url):
    """Тест сортировки новостей от самой свежей к самой старой."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, detail_url, news, comments):
    """Тест сортировки комментариев в хронологическом порядке."""
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
