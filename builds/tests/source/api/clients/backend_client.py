import allure
import requests

from api.clients.base_client import BaseClient
from api.common.exceptions import *
from api.common.methods import APIMethods


class BackendAPIClient(BaseClient):

    @property
    def post_headers(self):
        return {'Content-Type': 'application/x-www-form-urlencoded'}

    def post_registration(
            self,
            username: str,
            email: str,
            password: str,
            confirm: str,
            term: str,
            submit: str,
            raise_exception: bool = True
    ) -> requests.Response:

        headers = self.post_headers
        headers['Host'] = f'{self.host}:{self.port}'

        data = {
            'username': username,
            'email': email,
            'password': password,
            'confirm': confirm,
            'term': term,
            'submit': submit
        }
        
        response = self._request('reg',
                                 method=APIMethods.POST,
                                 headers=headers,
                                 data=data,
                                 expected_status=200,
                                 jsonify=False,
                                 raise_exception=raise_exception)

        session_cookie = [
            c.split('session=')[1] for c in response.request.headers['Cookie'].split(';') if c.startswith('session=')
        ]

        # Проверка существования куки.
        if len(session_cookie) == 0 or len(session_cookie[0]) == 0:
            raise CannotGetCookie(f'Cookie "session" does not exists.')

        return response

    def post_login(self, username: str, password: str, submit: str, raise_exception: bool = True) -> requests.Response:

        headers = self.post_headers
        headers['Host'] = f'{self.host}:{self.port}'

        data = {
            'username': username,
            'password': password,
            'submit': submit
        }

        response = self._request('login',
                                 method=APIMethods.POST,
                                 headers=headers,
                                 data=data,
                                 expected_status=200,
                                 jsonify=False,
                                 raise_exception=raise_exception)

        if self.session.cookies.get('session') is None:
            raise CannotGetCookie(f'Cookie "session" not set.')

        return response

    def get_logout(self, raise_exception: bool = True) -> requests.Response:
        headers = {
            'Cookie': f'session={self.session.cookies.get("session")}'
        }

        return self._request('logout',
                             headers=headers,
                             expected_status=200,
                             jsonify=False,
                             raise_exception=raise_exception)
