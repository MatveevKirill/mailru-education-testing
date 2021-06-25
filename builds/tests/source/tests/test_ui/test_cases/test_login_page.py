import pytest
import allure

from tests.test_ui.common.base_test_ui import BaseTestUI
from ui.pages.login_page import LoginPage
from utils.builder import Builder


class TestUILoginPositive(BaseTestUI):

    @pytest.mark.UI
    @allure.epic("UI Testing")
    @allure.feature("Login page")
    @allure.story("Correct login")
    @allure.description(
        """
        Описание: тестирование страницы авторизации для корректных данных.
        Ссылка: http://<APP_HOST>:<APP_PORT>/login
        Шаги:
            1) Создание тестового пользователя через БД;
            2) Авторизация в системе.
        Проверки:
            1) Проверка URL страницы.
        """
    )
    def test(self, user_positive: dict, login_page: LoginPage) -> None:
        self.create_user(user_positive)

        with allure.step("Авторизация пользователя"):
            login_page.login(user_positive['username'], user_positive['password'])

        with allure.step("Проверка URL страницы"):
            assert login_page.is_opened(is_opened_params={'new_url': f'{login_page.url}/welcome/'})


class TestUILoginNegative(BaseTestUI):

    @pytest.mark.UI
    @allure.epic("UI Testing")
    @allure.feature("Login page")
    @allure.story("Incorrect login")
    @allure.description(
        """
        Описание: тестирование страницы авторизации для некорректных данных.
        Ссылка: http://<APP_HOST>:<APP_PORT>/login
        Шаги:
            2) Авторизация в системе с некорректными данными.
        Проверки:
            1) Проверка URL страницы;
            2) Проверка сообщения об ошибке.
        """
    )
    @pytest.mark.parametrize(
        "user, message",
        [
            (Builder.user_data(), "Invalid username or password"),
            (Builder.user_data(username_length=17), "Incorrect username length"),
            (Builder.user_data(username_length=5), "Incorrect username length"),
            (Builder.user_data(password_length=5), "Incorrect password length"),
            (Builder.user_data(password_length=256), "Incorrect password length")
        ],
        ids=[
            "Invalid username or password",
            "Username length is 17",
            "Username length is 5",
            "Password length is 5",
            "Password length is 256"
        ]
    )
    def test(self, user: dict, message: str, login_page: LoginPage) -> None:
        with allure.step("Авторизация пользователя"):
            login_page.login(user['username'], user['password'])

        self.do_asserts([(True, login_page.is_opened(), "Проверка URL страницы"),
                         (login_page.get_error_msg(), message, "Проверка сообщения об ошибке")])
