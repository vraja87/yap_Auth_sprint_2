import uuid
from http import HTTPStatus

from src.tests.functional.settings import test_settings
from src.tests.functional.testdata.common_test_db_data import roles, users


async def test_create_role_admin_success(make_post_request_for_login, make_post_request):
    # Administrator authentication and token receipt
    admin_credentials = {"username": test_settings.superuser_login, "password": test_settings.superuser_passwd}
    login_response = await make_post_request_for_login('/api/v1/user/login', admin_credentials)
    access_token = login_response.body['access_token']

    role_data = {"name": "new_role", "description": "A new role"}

    headers = {"Authorization": f"Bearer {access_token}",
               "Content-Type": "application/json"}
    create_response = await make_post_request('/api/v1/roles/create', role_data, headers=headers)

    assert create_response.status == HTTPStatus.CREATED
    assert create_response.body['name'] == "new_role"


async def test_create_role_user_forbidden(make_post_request_for_login, make_post_request):
    # Authenticating a regular user and getting a token
    user_credentials = {"username": users[1][0], "password": users[1][1]}
    login_response = await make_post_request_for_login('/api/v1/user/login', user_credentials)
    access_token = login_response.body['access_token']

    role_data = {"name": "new_role_user", "description": "Role for a user"}
    headers = {"Authorization": f"Bearer {access_token}",
               "Content-Type": "application/json"}
    create_response = await make_post_request('/api/v1/roles/create', role_data, headers=headers)

    assert create_response.status == HTTPStatus.FORBIDDEN


async def test_delete_role_admin_success(make_post_request_for_login, make_post_request, make_delete_request):
    # Administrator authentication and creation of a new role
    admin_credentials = {"username": test_settings.superuser_login, "password": test_settings.superuser_passwd}
    login_response = await make_post_request_for_login('/api/v1/user/login', admin_credentials)
    access_token = login_response.body['access_token']

    role_data = {"name": "role_to_delete", "description": "Role to be deleted"}
    headers = {"Authorization": f"Bearer {access_token}",
               "Content-Type": "application/json"}
    create_response = await make_post_request('/api/v1/roles/create', role_data, headers=headers)

    role_id = create_response.body['id']

    # Deleting a created role
    delete_response = await make_delete_request(f'/api/v1/roles/delete/{role_id}', headers=headers)
    assert delete_response.status == HTTPStatus.NO_CONTENT


async def test_delete_role_user_forbidden(make_post_request_for_login, make_delete_request):
    # Authentication of a regular user
    user_credentials = {"username": users[1][0], "password": users[1][1]}
    login_response = await make_post_request_for_login('/api/v1/user/login', user_credentials)
    access_token = login_response.body['access_token']

    headers = {"Authorization": f"Bearer {access_token}",
               "Content-Type": "application/json"}

    some_uuid = str(uuid.uuid4())
    delete_response = await make_delete_request(f'/api/v1/roles/delete/{some_uuid}', headers=headers)

    assert delete_response.status == HTTPStatus.FORBIDDEN


async def test_get_all_roles_success(make_get_request):
    # Send a request to get all the roles
    response = await make_get_request('/api/v1/roles/')

    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    # Checking that there are certain roles in the response
    expected_roles = [role.name for role in roles]
    expected_roles.append(test_settings.superuser_role)

    for role in expected_roles:
        assert any(r['name'] == role for r in response.body)


async def test_get_role_by_id_success(make_post_request_for_login, make_get_request, make_post_request):
    # Administrator authentication and creation of a new role
    admin_credentials = {"username": test_settings.superuser_login, "password": test_settings.superuser_passwd}
    login_response = await make_post_request_for_login('/api/v1/user/login', admin_credentials)
    access_token = login_response.body['access_token']

    headers = {"Authorization": f"Bearer {access_token}"}
    role_id = roles[1].id

    # Getting information about the created role
    role_response = await make_get_request(f'/api/v1/roles/{role_id}', headers=headers)

    assert role_response.status == HTTPStatus.OK
    assert role_response.body['id'] == str(role_id)
    assert role_response.body['name'] == roles[1].name
    assert role_response.body['description'] == roles[1].description


async def test_get_nonexistent_role(make_get_request):
    # Attempt to get information about a non-existent role
    non_existent_role_id = str(uuid.uuid4())
    response = await make_get_request(f'/api/v1/roles/{non_existent_role_id}')

    assert response.status == HTTPStatus.NOT_FOUND


async def test_get_role_by_name_success(make_get_request):
    # Getting information about a role by name
    existing_role_name = roles[1].name

    role_response = await make_get_request(f'/api/v1/roles/{existing_role_name}/name')

    assert role_response.status == HTTPStatus.OK
    assert role_response.body['name'] == existing_role_name


async def test_get_nonexistent_role_by_name(make_get_request):
    nonexistent_role_name = "nonexistent_role"

    # Attempt to get information about a role with a non-existent name
    response = await make_get_request(f'/api/v1/roles/{nonexistent_role_name}/name')

    assert response.status == HTTPStatus.NOT_FOUND


async def test_get_user_roles_success(make_post_request_for_login, make_get_request):
    # User authentication
    credentials = {"username": users[0][0], "password": users[0][1]}
    login_response = await make_post_request_for_login('/api/v1/user/login', credentials)
    access_token = login_response.body['access_token']

    user_id = users[0][2].id

    # Getting user roles
    headers = {"Authorization": f"Bearer {access_token}"}
    roles_response = await make_get_request(f'/api/v1/roles/user/{user_id}', headers=headers)

    assert roles_response.status == HTTPStatus.OK
    assert isinstance(roles_response.body, list)
    assert [{'name': roles[0].name}] == roles_response.body


async def test_get_user_roles_forbidden(make_post_request_for_login, make_get_request):
    # Authentication of a regular user
    user_credentials = {"username": users[1][0], "password": users[1][1]}
    user_login_response = await make_post_request_for_login('/api/v1/user/login', user_credentials)
    user_access_token = user_login_response.body['access_token']

    # Trying to get another user's roles
    another_user_id = str(uuid.uuid4())  # UUID of another user
    headers = {"Authorization": f"Bearer {user_access_token}"}
    response = await make_get_request(f'/api/v1/roles/user/{another_user_id}', headers=headers)

    assert response.status == HTTPStatus.FORBIDDEN


async def test_assign_role_to_user_success(make_post_request_for_login, make_post_request):
    # Administrator authentication
    admin_credentials = {"username": test_settings.superuser_login, "password": test_settings.superuser_passwd}
    admin_login_response = await make_post_request_for_login('/api/v1/user/login', admin_credentials)
    admin_access_token = admin_login_response.body['access_token']

    # Assigning a new role to a user
    user_id = str(users[3][2].id)
    new_role_id = str(roles[1].id)
    assign_response = await make_post_request(
        path='/api/v1/roles/assign',
        query_data={"user_id": user_id, "role_id": new_role_id},
        headers={"Authorization": f"Bearer {admin_access_token}",
                 "Content-Type": "application/json"}
    )
    assert assign_response.status == HTTPStatus.OK
    assert any(roles[1].name == role["name"] for role in assign_response.body)


async def test_assign_role_user_forbidden(make_post_request_for_login, make_post_request):
    # Authentication of a regular user
    user_credentials = {"username": users[0][0], "password": users[0][1]}
    user_login_response = await make_post_request_for_login('/api/v1/user/login', user_credentials)
    user_access_token = user_login_response.body['access_token']

    # Attempt to assign a role to another user
    another_user_id = str(users[3][2].id)
    role_id = str(roles[1].id)
    response = await make_post_request(
        '/api/v1/roles/assign',
        {"user_id": another_user_id, "role_id": role_id},
        headers={"Authorization": f"Bearer {user_access_token}",
                 "Content-Type": "application/json"}
    )

    assert response.status == HTTPStatus.FORBIDDEN


async def test_detach_role_from_user_success(make_post_request_for_login, make_delete_request):
    # Administrator authentication
    admin_credentials = {"username": test_settings.superuser_login, "password": test_settings.superuser_passwd}
    admin_login_response = await make_post_request_for_login('/api/v1/user/login', admin_credentials)
    admin_access_token = admin_login_response.body['access_token']

    user_id = str(users[3][2].id)
    role_id = str(roles[1].id)

    # Attempt to detach role from user
    detach_role_data = {"user_id": user_id, "role_id": role_id}
    detach_response = await make_delete_request(
        '/api/v1/roles/detach',
        detach_role_data,
        headers={"Authorization": f"Bearer {admin_access_token}", "Content-Type": "application/json"}
    )

    assert detach_response.status == HTTPStatus.OK
    assert not any(roles[1].name == role["name"] for role in detach_response.body)
