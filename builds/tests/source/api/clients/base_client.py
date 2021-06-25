import logging
from urllib.parse import urljoin

import requests

from api.common.methods import APIMethods
from api.common.exceptions import *


logger = logging.getLogger('api-requests')


class BaseClient(object):
    session: requests.Session = None

    host: str = None
    port: int = None

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.session = requests.Session()

    def __del__(self):
        self.close_session()

    def __repr__(self):
        return f"<{self.__class__.__name__} (host='{self.host}'; port='{self.port}')>"

    @property
    def url(self):
        return f'http://{self.host}:{self.port}/'

    def close_session(self):
        if self.session is not None:
            self.session.close()

    def _request(
            self,
            url: str,
            method: str = APIMethods.GET,
            headers: dict = None,
            data: dict = None,
            params: dict = None,
            json: dict = None,
            files: dict = None,
            expected_status: int = 200,
            jsonify: bool = True,
            allow_redirects: bool = True,
            raise_exception: bool = True
    ):
        _url = urljoin(self.url, url)

        logger.info(
            f'REQUEST\n'
            f'Url: {_url}\n'
            f'Request headers: {headers}\n'
            f'Expected status: {expected_status}\n'
            f'Session cookies: {self.session.cookies.get_dict()}\n'
            f'Data: {data}\n'
            f'Json data: {json}\n'
            f'Files: {files}\n'
            f'Params data: {params}\n'
        )

        response = self.session.request(
            method,
            _url,
            headers=headers,
            data=data,
            params=params,
            json=json,
            allow_redirects=allow_redirects,
            files=files
        )

        logger.info(f'RESPONSE\n'
                    f'Response status: {response.status_code}\n'
                    f'Response headers: {response.headers}\n'
                    f'Request headers: {response.request.headers}\n'
                    f'Response url: {response.url}\n')

        if response.status_code != expected_status and raise_exception:
            raise ResponseStatusCodeException

        if jsonify:
            return response.json()
        else:
            return response

    def set_cookie(self, cookie_name: str, cookie_val: str):
        self.session.cookies.set(cookie_name, cookie_val, domain=f'http://{self.host}:{self.port}')
