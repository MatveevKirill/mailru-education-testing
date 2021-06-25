import pytest

from _pytest.fixtures import FixtureRequest
from selenium.webdriver.remote.webdriver import WebDriver

from utils.builder import MySQLBuilder
from tests.base_test_class import BaseTestClass
from api.clients.backend_client import BackendAPIClient


class BaseTestUI(BaseTestClass):
    driver: WebDriver = None
    configuration: dict = None
    mysql_builder: MySQLBuilder = None

    api_client: BackendAPIClient = None

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, request: FixtureRequest) -> None:
        self.driver = request.getfixturevalue('driver')
        self.api_client = request.getfixturevalue('backend_api_client')
        self.mysql_builder = MySQLBuilder(request.getfixturevalue('orm_client'))
        self.prepare()

    def create_user(self, user: dict, access: int = 1, active: int = 0) -> None:
        self.mysql_builder.create_user(username=user['username'],
                                       password=user['password'],
                                       email=user['email'],
                                       access=access,
                                       active=active)
