from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('home_url'),
         pytest.lazy_fixture('anonymous_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('detail_url'),
         pytest.lazy_fixture('anonymous_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('login_url'),
         pytest.lazy_fixture('anonymous_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('logout_url'),
         pytest.lazy_fixture('anonymous_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('signup_url'),
         pytest.lazy_fixture('anonymous_client'), HTTPStatus.OK),
    ),
)
def test_pages_availability(parametrized_client, url, expected_status):
    """Тест доступности страниц."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'redirect_url_prefix, redirect_url', (
        (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture('login_url')),
        (pytest.lazy_fixture('delete_url'), pytest.lazy_fixture('login_url'))
    )
)
def test_redirect_for_anonymous_client(redirect_url_prefix, redirect_url,
                                       anonymous_client):
    """
    Тест перенаправления анонимного пользователя на страницу
    авторизации при попытке перейти на страницу
    редактирования или удаления комментария.
    """
    expected_url = f'{redirect_url}?next={redirect_url_prefix}'
    response = anonymous_client.get(redirect_url_prefix)
    assertRedirects(response, expected_url)
