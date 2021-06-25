import os
import pytest

from _pytest.fixtures import Config, FixtureRequest, Parser

from tests.fixtures_test_data import *
from api.clients.openapi_client import OpenAPIClient
from api.clients.backend_client import BackendAPIClient
from orm.common.orm_client import ORMClient
from utils.func import rm_tree


def pytest_configure(config: Config) -> None:
    allure_report = config.getoption('--alluredir', '/tmp/allure-report')
    logs_report = '/tmp/logs'

    if not hasattr(config, 'workerinput'):

        if os.path.exists(allure_report):
            rm_tree(allure_report)
        else:
            os.mkdir(allure_report, mode=0o744)

        if os.path.exists(logs_report):
            rm_tree(logs_report)
        else:
            os.mkdir(logs_report, mode=0o744)

        with open(os.path.join(allure_report, 'environment.properties'), 'a') as f:
            f.write('\n'.join([f'{e}={os.environ[e]}' for e in os.environ]))

    config.allure_report = allure_report
    config.logs_report = logs_report


def pytest_addoption(parser: Parser) -> None:
    parser.addoption('--debugging', action="store_true")
    parser.addoption('--vnc', action="store_true")
    parser.addoption('--timeout-limit', default=5.0)


@pytest.fixture(scope="session")
def startup_options(request: FixtureRequest) -> dict:
    return {
        'debugging': request.config.getoption('--debugging')
    }


@pytest.fixture(scope="function")
def test_dir(request: FixtureRequest) -> str:
    test_name = request._pyfuncitem.nodeid.replace('/', '_').replace(':', '_')
    test_dir = os.path.join(request.config.logs_report, test_name)
    os.makedirs(test_dir, mode=0o744)
    return test_dir


@pytest.fixture(scope="session")
def app_connections() -> dict:
    return {
        'app_host': os.environ['APP_HOST'],
        'app_port': int(os.environ['APP_PORT'])
    }


@pytest.fixture(scope="session")
def mysql_connections() -> dict:
    return {
        'mysql_host': os.environ['MYSQL_HOST'],
        'mysql_port': int(os.environ['MYSQL_PORT']),
        'mysql_user': 'test_qa',
        'mysql_pass': 'qa_test',
        'mysql_data': 'appdb'
    }


@pytest.fixture(scope="session")
def orm_client(mysql_connections: dict) -> ORMClient:
    client = ORMClient()
    client.connect(host=mysql_connections['mysql_host'],
                   port=mysql_connections['mysql_port'],
                   username=mysql_connections['mysql_user'],
                   password=mysql_connections['mysql_pass'],
                   database=mysql_connections['mysql_data'])
    yield client
    client.disconnect()


@pytest.fixture(scope="session")
def abs_path() -> str:
    return os.path.abspath(os.path.join(__file__, os.pardir))


@pytest.fixture(scope="session")
def driver_configuration(request: FixtureRequest) -> dict:
    return {
        'vnc': request.config.getoption('--vnc'),
        'selenoid': f'http://{os.environ["SELENOID_HOST"]}/wd/hub'
    }


@pytest.fixture(scope="session")
def page_configuration(request: FixtureRequest) -> dict:
    return {
        'timeout_limit': request.config.getoption('--timeout-limit')
    }


@pytest.fixture(scope="function")
def open_api_client(app_connections: dict) -> OpenAPIClient:
    return OpenAPIClient(app_connections['app_host'], app_connections['app_port'])


@pytest.fixture(scope="function")
def backend_api_client(app_connections: dict) -> BackendAPIClient:
    return BackendAPIClient(app_connections['app_host'], app_connections['app_port'])
