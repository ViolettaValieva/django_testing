from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from .constants import (
    ANONYMOUS_CLIENT,
    AUTHOR_CLIENT,
    DELETE_URL,
    DETAIL_URL,
    EDIT_URL,
    HOME_URL,
    LOGIN_URL,
    LOGOUT_URL,
    READER_CLIENT,
    SIGNUP_URL,
)


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (HOME_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (DETAIL_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, READER_CLIENT, HTTPStatus.NOT_FOUND),
        (EDIT_URL, READER_CLIENT, HTTPStatus.NOT_FOUND),
        (LOGIN_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
    ),
)
def test_pages_availability(parametrized_client, url, expected_status):
    """Тест доступности страниц."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'redirect_url_prefix, redirect_url', (
        (EDIT_URL, LOGIN_URL),
        (DELETE_URL, LOGIN_URL)
    )
)
def test_redirect_for_anonymous_client(redirect_url_prefix, redirect_url,
                                       anonymous_client):
    """Тест перенаправления анонимного пользователя на страницу авторизации."""
    expected_url = f'{redirect_url}?next={redirect_url_prefix}'
    response = anonymous_client.get(redirect_url_prefix)
    assertRedirects(response, expected_url)
