import os
import pytest
import allure
import logging

from _pytest.fixtures import FixtureRequest
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver

from ui.pages.login_page import LoginPage
from ui.pages.registration_page import RegistrationPage
from utils.func import create_logger


@pytest.fixture(scope="function")
def login_page(driver: WebDriver, page_configuration: dict) -> LoginPage:
    return LoginPage(driver, page_configuration)


@pytest.fixture(scope="function")
def registration_page(login_page: LoginPage) -> RegistrationPage:
    return login_page.go_to_registration()


@pytest.fixture(scope="function")
def driver(driver_configuration: dict, test_dir: str) -> WebDriver:
    options = ChromeOptions()
    options.add_experimental_option("prefs", {"profile.default_content_settings.popups": 0})

    caps = {
        'browserName': 'chrome',
        'version': '90.0',
        'sessionTimeout': '2m',
        "selenoid:options": {
            "enableVNC": True,
            "enableVideo": False
        }
    }

    browser = webdriver.Remote(driver_configuration['selenoid'], options=options, desired_capabilities=caps)
    browser.maximize_window()
    browser.get(f'http://{os.environ["APP_HOST"]}:{os.environ["APP_PORT"]}/')
    yield browser
    browser.quit()


@pytest.fixture(scope='function', autouse=True)
def ui_report(driver: WebDriver, request: FixtureRequest, test_dir: str, startup_options: dict) -> logging.Logger:
    logs = [('ui-logging.log', 'ui-logger'), ('mysql-logging.log', 'mysql-logger')]
    loggers = list(map(lambda x: create_logger(test_dir, x[0], x[1]), logs))
    failed_tests_count = request.session.testsfailed

    yield

    for logger in loggers:
        for handler in logger.handlers:
            handler.close()

    for log in logs:
        with open(os.path.join(test_dir, log[0]), 'r') as f:
            allure.attach(f.read(), log[0], attachment_type=allure.attachment_type.TEXT)

    if request.session.testsfailed > failed_tests_count:
        screenshot_file = os.path.join(test_dir, 'failure.png')
        driver.get_screenshot_as_file(screenshot_file)
        allure.attach.file(screenshot_file, 'failure.png', attachment_type=allure.attachment_type.PNG)

        browser_logfile = os.path.join(test_dir, 'browser.log')
        with open(browser_logfile, 'w') as f:
            for i in driver.get_log('browser'):
                f.write(f"{i['level']} - {i['source']}\n{i['message']}\n\n")

        with open(browser_logfile, 'r') as f:
            allure.attach(f.read(), 'browser.log', attachment_type=allure.attachment_type.TEXT)
