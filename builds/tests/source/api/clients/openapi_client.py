import requests

from api.common.methods import APIMethods
from api.clients.base_client import BaseClient


class OpenAPIClient(BaseClient):

    @property
    def post_headers(self):
        return {'Content-Type': 'application/json'}

    def post_add_user(self, username: str, password: str, email: str, raise_exception: bool = True) -> requests.Response:

        headers = self.post_headers
        headers['Cookie'] = f'session={self.session.cookies.get("session")}'

        data = {
            'username': username,
            'password': password,
            'email': email
        }

        return self._request('api/add_user',
                             method=APIMethods.POST,
                             headers=headers,
                             json=data,
                             jsonify=False,
                             expected_status=201,
                             raise_exception=raise_exception)

    def get_delete_user(self, username: str, raise_exception: bool = True) -> requests.Response:
        headers = self.post_headers
        headers['Cookie'] = f'session={self.session.cookies.get("session")}'

        return self._request(f'api/del_user/{username}',
                             headers=headers,
                             expected_status=204,
                             jsonify=False,
                             raise_exception=raise_exception)

    def get_block_user(self, username: str, raise_exception: bool = True) -> requests.Response:
        headers = self.post_headers
        headers['Cookie'] = f'session={self.session.cookies.get("session")}'

        return self._request(f'api/block_user/{username}',
                             headers=headers,
                             expected_status=200,
                             jsonify=False,
                             raise_exception=raise_exception)

    def get_accept_user(self, username: str, raise_exception: bool = True) -> requests.Response:
        headers = self.post_headers
        headers['Cookie'] = f'session={self.session.cookies.get("session")}'

        return self._request(f'api/accept_user/{username}',
                             headers=headers,
                             expected_status=200,
                             jsonify=False,
                             raise_exception=raise_exception)
