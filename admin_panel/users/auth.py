import uuid
from http import HTTPStatus

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        """
        Checks the existence of the user in the auth service, creates django in the db if necessary

        if auth service unavailable, will try to find user in local db.
        """
        url = 'http://auth-api:8000/api/v1/user/login'
        payload = {'username': username, 'password': password}
        headers = {'X-Request-Id': str(uuid.uuid4())}
        try:
            response = requests.post(url, headers=headers, data=payload)
        except requests.RequestException as e:
            logger.warning(f"Connection error to auth-api service: {e}")
            user = User.objects.get(username=username)
            if user:
                logger.warning(f"accept user {username} authentification in local mode")
                return user
            else:
                return None

        if response.status_code != HTTPStatus.OK:
            return None

        data = response.json()
        try:
            user, created = User.objects.get_or_create(username=data['login'],)
            user.username = username
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.is_admin = any(role_name == "admin" for role_name in data.get('roles'))
            user.is_active = True
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
