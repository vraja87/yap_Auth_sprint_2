from asyncio import sleep
from http import HTTPStatus

import pytest


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Positive tests
        (
                {'login': 'Aa1',
                 'password': 'aAa_0',
                 'first_name': 'Li',
                 'last_name': 'Po',
                 },
                {'status': HTTPStatus.CREATED, 'length': 5}
        ),
        # Negative tests
        # Missed login
        (
            {'password': 'password2',
             'first_name': 'First',
             'last_name': 'Last'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1},
        ),
        # Missed password
        (
            {'login': 'UserTwoCreate',
             'first_name': 'First',
             'last_name': 'Last'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1},
        ),
        # Too short password
        (
            {'login': 'UserThreeCreate',
             'password': 'pass',
             'first_name': 'First',
             'last_name': 'Last'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1},
        ),
        # wrong password format. No capital case
        (
            {'login': 'UserThreeCreate',
             'password': 'aaa_0',
             'first_name': 'First',
             'last_name': 'Last'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1},
        ),
        # Inalid login (spaces)
        (
            {'login': 'invalid login',
             'password': 'password3',
             'first_name': 'First',
             'last_name': 'Last'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1},
        ),
        # User already exist
        (
            {'login': 'Aa1',
             'password': 'aAa_0',
             'first_name': 'Li',
             'last_name': 'Po',
             },
            {'status': HTTPStatus.CONFLICT, 'length': 1},
        ),
    ]
)
async def test_create_login(make_post_request, query_data: dict, expected_answer: dict):
    response = await make_post_request('/api/v1/user/signup', query_data)

    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


async def test_login_success(make_post_request_for_login):
    # Используем данные пользователя с ролью администратора
    credentials = {
        "username": "UserAdmin",  # Логин администратора
        "password": "Some_Pass1"        # Пароль администратора
    }
    response = await make_post_request_for_login('/api/v1/user/login', credentials)

    assert response.status == HTTPStatus.OK
    assert 'access_token' in response.body
    assert 'refresh_token' in response.body


async def test_login_invalid_credentials(make_post_request_for_login):
    # Используем неверные учетные данные
    invalid_credentials = {
        "username": "UserAdmin",
        "password": "wrongpassword"
    }
    response = await make_post_request_for_login('/api/v1/user/login', invalid_credentials)

    assert response.status == HTTPStatus.UNAUTHORIZED
    assert "Wrong login or password" in response.body['detail']


async def test_logout_success(make_post_request_for_login, make_post_request):
    credentials = {"username": "UserAdmin", "password": "Some_Pass1"}
    login_response = await make_post_request_for_login('/api/v1/user/login', credentials)
    access_token = login_response.body['access_token']

    headers = {"Authorization": f"Bearer {access_token}"}
    logout_response = await make_post_request('/api/v1/user/logout', headers=headers)

    assert logout_response.status == HTTPStatus.OK
    assert logout_response.body['message'] == "Successfully logged out"


async def test_logout_with_invalid_token(make_post_request):
    invalid_token = "some_invalid_token"
    response = await make_post_request('/api/v1/user/logout', {"access_token": invalid_token})
    assert response.status == HTTPStatus.FORBIDDEN
    assert response.body['detail'] == "Not authenticated"


async def test_logout_all_success(make_post_request_for_login, make_post_request):
    # login again
    credentials = {"username": "UserAdmin", "password": "Some_Pass1"}
    login_response = await make_post_request_for_login('/api/v1/user/login', credentials)
    access_token = login_response.body['access_token']

    # exit all sessions
    headers = {"Authorization": f"Bearer {access_token}"}
    logout_all_response = await make_post_request('/api/v1/user/logout_all', headers=headers, query_data=None)

    assert logout_all_response.status == HTTPStatus.OK
    assert logout_all_response.body['message'] == "Successfully logged out from all sessions"

    # try some api with same token... logout again.
    response = await make_post_request('/api/v1/user/logout', {"access_token": access_token})

    assert response.status == HTTPStatus.FORBIDDEN
    assert response.body['detail'] == "Not authenticated"


async def test_refresh_tokens_success(make_post_request_for_login, make_post_request__form_data):
    # login again
    credentials = {"username": "UserAdmin", "password": "Some_Pass1"}
    login_response = await make_post_request_for_login('/api/v1/user/login', credentials)
    refresh_token = login_response.body['refresh_token']

    await sleep(2)  # need some delay to get different refresh token
    refresh_response = await make_post_request__form_data('/api/v1/user/refresh', {"refresh_token": refresh_token})

    assert refresh_response.status == HTTPStatus.OK
    assert 'access_token' in refresh_response.body
    assert 'refresh_token' in refresh_response.body
    assert refresh_response.body['refresh_token'] != refresh_token


async def test_refresh_with_invalid_token(make_post_request__form_data):
    # use invalid refresh token.
    invalid_token = "some_invalid_token"
    response = await make_post_request__form_data('/api/v1/user/refresh', {"refresh_token": invalid_token})

    assert response.status == HTTPStatus.UNAUTHORIZED
    assert response.body['detail'] == "Invalid refresh token"


async def test_get_login_history_success(make_post_request_for_login, make_get_request):
    # login again
    credentials = {"username": "UserAdmin", "password": "Some_Pass1"}
    login_response = await make_post_request_for_login('/api/v1/user/login', credentials)
    access_token = login_response.body['access_token']

    headers = {"Authorization": f"Bearer {access_token}"}
    history_response = await make_get_request('/api/v1/user/login-history', headers=headers)

    assert history_response.status == HTTPStatus.OK
    assert isinstance(history_response.body, list)
    assert len(history_response.body) >= 1
    assert 'user_agent' in history_response.body[0]
    assert 'ip_address' in history_response.body[0]
    assert 'login_date' in history_response.body[0]
    assert len(history_response.body[0]) == 3


async def test_get_login_history_unauthorized(make_get_request):
    # Attempt to get login history without authorization
    response = await make_get_request('/api/v1/user/login-history')

    assert response.status == HTTPStatus.FORBIDDEN
    assert response.body['detail'] == "Not authenticated"


async def test_update_user_success(make_post_request_for_login, make_patch_request):
    credentials = {"username": "UserAdmin", "password": "Some_Pass1"}
    login_response = await make_post_request_for_login('/api/v1/user/login', credentials)
    access_token = login_response.body['access_token']

    user_update = {
        "login": "NewUserAdmin",
        "password": "New_Pass1",
        "first_name": "NewFirstName",
        "last_name": "NewLastName"
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    update_response = await make_patch_request('/api/v1/user/update', user_update, headers=headers)

    assert update_response.status == HTTPStatus.OK
    assert update_response.body['message'] == "User information successfully updated"

    user_update = {
        "login": "UserAdmin",
        "password": "Some_Pass1",
        "first_name": "FirstName",
        "last_name": "LastName"
    }
    await make_patch_request('/api/v1/user/update', user_update, headers=headers)


async def test_update_user_unauthorized(make_patch_request):
    user_update = {"login": "new_login", "password": "new_password"}
    response = await make_patch_request('/api/v1/user/update', user_update)

    assert response.status == HTTPStatus.FORBIDDEN


async def test_get_access_roles_success(make_post_request_for_login, make_get_request):
    credentials = {"username": "UserAdmin", "password": "Some_Pass1"}
    login_response = await make_post_request_for_login('/api/v1/user/login', credentials)
    access_token = login_response.body['access_token']

    headers = {"Authorization": f"Bearer {access_token}"}
    roles_response = await make_get_request('/api/v1/user/access-roles', headers=headers)

    assert roles_response.status == HTTPStatus.OK
    assert isinstance(roles_response.body, list)
    assert {'name': 'administrator'} == roles_response.body[0]


async def test_get_access_roles_unauthorized(make_get_request):
    response = await make_get_request('/api/v1/user/access-roles')

    assert response.status == HTTPStatus.FORBIDDEN
