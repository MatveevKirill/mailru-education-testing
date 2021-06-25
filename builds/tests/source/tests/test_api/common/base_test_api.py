import pytest
import allure
import requests
from _pytest.fixtures import FixtureRequest

from api.clients.openapi_client import OpenAPIClient
from api.clients.backend_client import BackendAPIClient
from orm.common.orm_client import ORMClient
from tests.base_test_class import BaseTestClass
from utils.builder import MySQLBuilder


@allure.step
def cookies(**kwargs):
    pass


class BaseTestAPI(BaseTestClass):
    open_api_client: OpenAPIClient = None
    backend_api_client: BackendAPIClient = None
    orm_client: ORMClient = None
    mysql_builder: MySQLBuilder = None

    @staticmethod
    def execute_http_query(method, raise_exception: bool = True, *args, **kwargs) -> requests.Response:
        r: requests.Response = method(*args, raise_exception=raise_exception, **kwargs)

        # Добавление куки
        session_cookie = [
            c.split('session=')[1] for c in r.request.headers['Cookie'].split(';') if c.startswith('session=')
        ]
        if len(session_cookie) == 1 and len(session_cookie[0]) > 0:
            cookies(
                name="session",
                value=session_cookie[0]
            )

        # Добавление ответа в зависимости от формата.
        if 'Content-Type' in r.headers:
            if r.headers['Content-Type'].split(';')[0] == "text/html":
                allure.attach(r.text, 'response.html', allure.attachment_type.HTML)
            elif r.headers['Content-Type'].split(';')[0] == "application/json":
                allure.attach(r.text, 'response.json', allure.attachment_type.JSON)
            else:
                allure.attach(r.text, 'response.txt', allure.attachment_type.TEXT)

        return r

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, request: FixtureRequest) -> None:
        self.orm_client = request.getfixturevalue('orm_client')
        self.open_api_client = request.getfixturevalue('open_api_client')
        self.backend_api_client = request.getfixturevalue('backend_api_client')
        self.mysql_builder = MySQLBuilder(self.orm_client)
        self.prepare()

    def create_user(self, user: dict, access: int = 1, active: int = 0) -> None:
        self.mysql_builder.create_user(username=user['username'], password=user['password'],
                                       email=user['email'], access=access, active=active)
