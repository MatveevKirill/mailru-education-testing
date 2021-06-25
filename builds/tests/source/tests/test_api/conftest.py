import os
import pytest
import allure
import logging

from api.clients.backend_client import BackendAPIClient
from utils.func import create_logger


@pytest.fixture(scope="function")
def backend_api_client(app_connections: dict) -> BackendAPIClient:
    return BackendAPIClient(app_connections['app_host'], app_connections['app_port'])


@pytest.fixture(scope="function", autouse=True)
def api_logger(test_dir: str, startup_options: dict) -> logging.Logger:
    logger = create_logger(test_dir, 'api-requests.log', 'api-requests')

    yield

    for handler in logger.handlers:
        handler.close()

    with open(os.path.join(test_dir, 'api-requests.log'), 'r') as f:
        allure.attach(f.read(), 'api-requests.log', attachment_type=allure.attachment_type.TEXT)
