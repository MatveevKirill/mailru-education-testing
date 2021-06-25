import os
import pytest
import allure

from tests.test_ui.common.base_test_ui import BaseTestUI
from ui.pages.registration_page import RegistrationPage
from utils.builder import Builder


class PrepareRegistrationTests(BaseTestUI):
    _registration_page: RegistrationPage = None

    @pytest.fixture(scope="function", autouse=True)
    def prepare_test(self, registration_page: RegistrationPage) -> None:
        self._registration_page = registration_page


class TestUIRegistrationPositive(PrepareRegistrationTests):

    @pytest.mark.UI
    @allure.epic("UI Testing")
    @allure.feature("Registration page")
    @allure.story("Correct registration")
    @allure.description(
        """
        Описание: тестирование страницы регистрации для корректных данных.
        Ссылка: http://<APP_HOST>:<APP_PORT>/reg
        Шаги:
            1) Регистрация пользователя.
        Проверки:
            1) Проверка URL для проверки.
        """
    )
    def test(self, user_positive: dict) -> None:
        with allure.step("Регистрация пользователя"):
            self._registration_page.registration(**user_positive)

        with allure.step("Проверка URL страницы"):
            assert self._registration_page.is_opened(is_opened_params={'new_url': f'http://{os.environ["APP_HOST"]}:{os.environ["APP_PORT"]}/welcome/'})


class TestUIRegistrationNegative(PrepareRegistrationTests):

    @pytest.mark.UI
    @allure.epic("UI Testing")
    @allure.feature("Registration page")
    @allure.story("Incorrect registration")
    @allure.description(
        """
        Описание: тестирование страницы регистрации для некорректных данных.
        Ссылка: http://<APP_HOST>:<APP_PORT>/reg
        Шаги:
            1) Регистрация пользователя.
        Проверки:
            1) 
        """
    )
    @pytest.mark.parametrize(
        "user, message",
        [
            (Builder.user_data(confirm_user_password=False), 'Passwords must match'),
            (Builder.user_data(username_length=5), 'Incorrect username length'),
            (Builder.user_data(username_length=17), 'Incorrect username length'),
            (Builder.user_data(validate_email=False), 'Invalid email address'),
            (Builder.user_data(email_length=65), 'Incorrect email length'),
            (Builder.user_data(password_length=5), 'Incorrect password length'),
            (Builder.user_data(password_length=256), 'Incorrect password length'),
            (Builder.user_data(validate_email=False, email_length=5, username_length=4), 'Incorrect email and username')
        ],
        ids=[
            'Incorrect passwords',
            'Username length is 5',
            'Username length is 17',
            'Incorrect email',
            'Email length is 65',
            'Password length is 5',
            'Password length is 256',
            'Incorrect username and email'
        ]
    )
    def test(self, user: dict, message: str) -> None:
        with allure.step("Регистрация пользователя"):
            self._registration_page.registration(**user)

        self.do_asserts([(True, self._registration_page.is_opened(), "Проверка URL страницы"),
                         (self._registration_page.get_error_msg(), message, "Проверка сообщения об ошибке")])
