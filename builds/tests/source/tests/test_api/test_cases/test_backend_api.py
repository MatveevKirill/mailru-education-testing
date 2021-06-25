import pytest
import allure
import typing

from urllib.parse import urljoin

import requests

from tests.test_api.common.base_test_api import BaseTestAPI
from orm.models.MYSQL_DB import ModelTestUsers
from api.common.exceptions import *
from utils.builder import Builder


class TestBackendAPIClientRegistrationPositive(BaseTestAPI):

    @pytest.fixture(scope="function")
    def prepare_create_user(self, user_positive: dict) -> typing.Tuple[ModelTestUsers, ModelTestUsers]:
        # Создание модели пользователя.
        model_user = ModelTestUsers(username=user_positive['username'],
                                    password=user_positive['password'],
                                    email=user_positive['email'],
                                    access=1,
                                    active=0)

        # Выполнение запроса на регистрацию пользователя.
        self.execute_http_query(self.backend_api_client.post_registration, **user_positive, term='y', submit='Register')

        # Получение результата из БД.
        user_from_db = self.orm_client.session.query(ModelTestUsers).filter_by(username=user_positive['username']).one()
        self.orm_client.session.commit()
        return model_user, user_from_db

    @pytest.mark.API
    @pytest.mark.API_BACKEND
    @allure.epic("API Testing")
    @allure.feature("API Backend")
    @allure.story("Correct registration")
    @allure.description(
        """
        Описание: тестирование регистрации пользователя по корректным данным.
        Ссылка: http://<APP_HOST>:<APP_PORT>/reg
        Метод: POST
        Шаги:
            1) Создание пользователя;
            2) Получение из БД созданного пользователя.
        Проверки:
            1) Статус код: 200;
            2) Сообщение о создании сущности.
        """
    )
    def test(self, prepare_create_user: typing.Tuple[ModelTestUsers, ModelTestUsers]) -> None:
        with allure.step("Проверка добавления тестового пользователя в БД"):
            assert prepare_create_user[0] == prepare_create_user[1]


class TestBackendAPIClientRegistrationNegative(BaseTestAPI):

    @pytest.mark.API
    @pytest.mark.API_BACKEND
    @allure.epic("API Testing")
    @allure.feature("API Backend")
    @allure.story("Incorrect registration")
    @allure.description(
        """
        Описание: тестирование регистрации пользователя по некорректным данным.
        Ссылка: http://<APP_HOST>:<APP_PORT>/reg
        Метод: POST
        Шаги:
            1) Выполнение некорректного запроса.
        Проверки:
            1) Вызов ошибки ResponseStatusCodeException.
        """
    )
    @pytest.mark.parametrize(
        "user, term, submit",
        [
            (Builder.user_data(), 'Nope', 'Register'),
            (Builder.user_data(), '', 'Register'),
            (Builder.user_data(), 'y', 'NotWorking'),
            (Builder.user_data(), 'y', ''),
            (Builder.user_data(confirm_user_password=False), 'y', 'Register'),
            (Builder.user_data(username_length=5), 'y', 'Register'),
            (Builder.user_data(username_length=17), 'y', 'Register'),
            (Builder.user_data(validate_email=False), 'y', 'Register'),
            (Builder.user_data(email_length=65), 'y', 'Register'),
            (Builder.user_data(password_length=5), 'y', 'Register'),
            (Builder.user_data(password_length=256), 'y', 'Register')
        ],
        ids=[
            'Incorrect term field',
            'Null term field',
            'Incorrect submit field',
            'Null submit field',
            'Incorrect passwords',
            'Username length is 5',
            'Username length is 17',
            'Incorrect email',
            'Email length is 65',
            'Password length is 5',
            'Password length is 256'
        ]
    )
    def test_registration_user_negative(self, user: dict, term: str, submit: str) -> None:
        with pytest.raises(ResponseStatusCodeException):
            self.execute_http_query(self.backend_api_client.post_registration, **user, term=term, submit=submit)
            pytest.fail(f'Не вызвано исключение типа "ResponseStatusCodeException"')

    @pytest.mark.API
    @pytest.mark.API_BACKEND
    @allure.epic("API Testing")
    @allure.feature("API Backend")
    @allure.story("Incorrect registration")
    @allure.description(
        """
        Описание: тестирование безопасности сервиса.
        Ссылка: http://<APP_HOST>:<APP_PORT>/reg
        Метод: POST
        Шаги:
            1) Выполнения запроса по некорректным данным.
        Проверки:
            1) Вызывается исключение ResponseStatusCodeException.
        """
    )
    def test_registration_security_negative(self, negative_attack_user: dict) -> None:
        with pytest.raises(ResponseStatusCodeException):
            self.execute_http_query(self.backend_api_client.post_registration,
                                    **negative_attack_user,
                                    term='y',
                                    submit='Register')
            pytest.fail(f'Не вызвано исключение типа "ResponseStatusCodeException"')

    @pytest.mark.API
    @pytest.mark.API_BACKEND
    @allure.epic("API Testing")
    @allure.feature("API Backend")
    @allure.story("Incorrect registration")
    @allure.title("Test registration for exists user")
    @allure.description(
        """
        Описание: повторная регистрация для пользователя.
        Ссылка: http://<APP_HOST>:<APP_PORT>/reg
        Метод: POST
        Шаги:
            1) Создание тестового пользователя;
            2) Попытка создать нового пользователя по таким же данным.
        Проверки:
            1) Вызывается исключение ResponseStatusCodeException.
        """
    )
    @pytest.mark.parametrize("user", [Builder.user_data()], ids=["Correct user credentials"])
    def test_registration_for_exists_user(self, user: dict) -> None:
        self.create_user(user)
        with pytest.raises(ResponseStatusCodeException):
            self.execute_http_query(self.backend_api_client.post_registration, **user, term='y', submit='Register')
            pytest.fail(f'Не вызвано исключение типа "ResponseStatusCodeException"')


class TestBackendAPIClientLoginPositive(BaseTestAPI):

    @pytest.fixture(scope="function")
    def prepare_data(self, user_positive: dict) -> requests.Response:
        # Создание тестового пользователя.
        self.create_user(user_positive)

        # Выполнение запроса на авторизацию пользователя.
        return self.execute_http_query(self.backend_api_client.post_login,
                                       username=user_positive['username'],
                                       password=user_positive['password'],
                                       submit='Login')

    @pytest.mark.API
    @pytest.mark.API_BACKEND
    @allure.epic("API Testing")
    @allure.feature("API Backend")
    @allure.story("Correct login")
    @allure.description(
        """
        Описание: авторизация для пользователя с корректными данными.
        Ссылка: http://<APP_HOST>:<APP_PORT>/login
        Метод: POST
        Шаги:
            1) Добавление тестового пользователя в БД;
            2) Выполнение запроса на авторизацию.
        Проверки:
            1) Проверка статус кода: 200;
            2) Проверка URL после авторизации.
        """
    )
    def test(self, prepare_data: requests.Response) -> None:
        self.do_asserts([(prepare_data.status_code, 200, "Проверка статус кода"),
                         (prepare_data.url, urljoin(self.backend_api_client.url, 'welcome/'), "Проверка url")])


class TestBackendAPIClientLoginNegative(BaseTestAPI):
    @pytest.mark.API
    @pytest.mark.API_BACKEND
    @allure.epic("API Testing")
    @allure.feature("API Backend")
    @allure.story("Incorrect login")
    @allure.description(
        """
        Описание: авторизация для пользователя с некорректными данными.
        Ссылка: http://<APP_HOST>:<APP_PORT>/login
        Метод: POST
        Шаги:
            1) Регистрация тестового пользователя;
            2) Выполнение запроса на авторизацию.
        Проверки:
            1) Проверка вызова ошибки: ResponseStatusCodeException.
        """
    )
    @pytest.mark.parametrize(
        "user, submit",
        [
            (Builder.user_data(), ''),
            (Builder.user_data(password_length=5), 'Login')
        ],
        ids=[
            'Submit is null',
            'Password length is 5'
        ]
    )
    def test(self, user: dict, submit: str) -> None:
        self.create_user(user)
        with pytest.raises(ResponseStatusCodeException):
            self.execute_http_query(self.backend_api_client.post_login,
                                    username=user['username'],
                                    password=user['password'],
                                    submit=submit)
            pytest.fail(f'Не вызвано исключение типа "ResponseStatusCodeException"')


class TestBackendAPIClientLoginForNotExistsUserNegative(BaseTestAPI):

    @pytest.mark.API
    @pytest.mark.API_BACKEND
    @allure.epic("API Testing")
    @allure.feature("API Backend")
    @allure.story("Incorrect login")
    @allure.description(
        """
        Описание: авторизация для несуществующего пользователя.
        Ссылка: http://<APP_HOST>:<APP_PORT>/login
        Метод: POST
        Шаги:
            1) Выполнение запроса на авторизацию.
        Проверки:
            1) Проверка вызова ошибки: CannotGetCookie.
        """
    )
    @pytest.mark.parametrize("user", [Builder.user_data()], ids=["Correct credentials for not exists user"])
    def test(self, user: dict) -> None:
        with pytest.raises(ResponseStatusCodeException):
            self.execute_http_query(self.backend_api_client.post_login,
                                    username=user['username'],
                                    password=user['password'],
                                    submit='Register')
            pytest.fail(f'Не вызвано исключение типа "ResponseStatusCodeException"')


class TestBackendAPIClientLogoutPositive(TestBackendAPIClientRegistrationPositive):
    _response: requests.Response = None

    def prepare(self) -> None:
        # Переопределение базового метода.
        super(TestBackendAPIClientLogoutPositive, self).prepare()

        # Создание модели пользователя.
        user = Builder.user_data()

        # Создание пользователя в БД.
        self.create_user(user)
        
        # Авторизация пользователя.
        self.backend_api_client.post_login(username=user['username'], password=user['password'], submit='Login')

        # Выход из аккаунта
        self._response = self.backend_api_client.get_logout(raise_exception=False)

    @pytest.mark.API
    @pytest.mark.API_BACKEND
    @allure.epic("API Testing")
    @allure.feature("API Backend")
    @allure.story("Correct logout")
    @allure.description(
        """
        Описание: выход из системы по корректным данным.
        Ссылка: http://<APP_HOST>:<APP_PORT>/logout
        Метод: POST
        Шаги:
            1) Регистрация тестового пользователя;
            2) Выход из системы.
        Проверки:
            1) Проверка статус кода;
            2) Проверка URL после выхода.
        """
    )
    def test(self) -> None:
        self.do_asserts([(self._response.status_code, 200, "Проверка статус кода"),
                         (self._response.url, f'{self.backend_api_client.url}login', "Проверка URL после выхода")])


class TestBackendAPIClientLogoutNegative(BaseTestAPI):

    @pytest.mark.API
    @pytest.mark.API_BACKEND
    @allure.epic("API Testing")
    @allure.feature("API Backend")
    @allure.story("Incorrect logout")
    @allure.description(
        """
        Описание: выход из системы под неавторизованным пользователем.
        Ссылка: http://<APP_HOST>:<APP_PORT>/logout
        Метод: POST
        Шаги:
            1) Выход из системы.
        Проверки:
            1) Проверка статус кода;
            2) Проверка URL после выхода.
        """
    )
    def test_incorrect_logout(self):
        with pytest.raises(ResponseStatusCodeException):
            self.execute_http_query(self.backend_api_client.post_logout, raise_exception=False)
            pytest.fail('Не вызвано исключение типа: "ResponseStatusCodeException"')
