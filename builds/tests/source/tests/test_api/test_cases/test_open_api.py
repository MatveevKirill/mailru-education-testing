import pytest
import allure
import json
import requests
import typing

from orm.models.MYSQL_DB import ModelTestUsers
from tests.test_api.common.base_test_api import BaseTestAPI
from api.common.exceptions import *

from utils.builder import Builder


class PrepareOpenAPIClient(BaseTestAPI):
    CREATE_USER: bool = True

    def prepare(self) -> None:
        if self.CREATE_USER:
            with allure.step("Создание сервисного пользователя"):
                self.backend_api_client.post_registration(**Builder.user_data(), term='y', submit='Register')
                self.open_api_client.set_cookie('session', self.backend_api_client.session.cookies.get('session'))

    def do_incorrect_query(self, method, params: str, **kwargs) -> None:
        r = self.execute_http_query(method=method, raise_exception=False, **kwargs)
        j = json.loads(r.text)

        self.do_asserts([(r.status_code, 401, "Проверка статус кода"),
                         (j['error'], 'session lifetime expires', "Проверка сообщения об ошибке"),
                         (j['url'],
                          f'http://{self.open_api_client.host}:{self.open_api_client.port}/api/{params}',
                          "Проверка Url запроса")])


class TestOpenAPIClientAddUserPositive(PrepareOpenAPIClient):

    def add_user(self, user: dict) -> requests.Response:
        # Создание модели пользователя.
        model = ModelTestUsers(username=user['username'],
                               password=user['password'],
                               email=user['email'],
                               access=1,
                               active=0)

        # Выполнение запроса на создание пользователя.
        r = self.execute_http_query(self.open_api_client.post_add_user,
                                    username=user['username'],
                                    password=user['password'],
                                    email=user['email'],
                                    raise_exception=False)

        # Получение пользователя из БД.
        m = self.orm_client.session.query(ModelTestUsers).filter_by(username=user['username']).all()
        self.orm_client.session.commit()
        
        # Проверка пользователя.
        if len(m) == 1:
            with allure.step("Проверка пользователя"):
                assert m[0] == model
        elif len(m) > 1:
            raise AssertionError('БД возвращает больше 1 строки.')

        return r

    @pytest.fixture(scope="function")
    def add_user_response(self, user_positive: dict) -> requests.Response:
        return self.add_user(user_positive)

    @pytest.mark.API
    @pytest.mark.API_OPEN
    @allure.epic("API Testing")
    @allure.feature("API Open")
    @allure.story("Correct user addition")
    @allure.description(
        """
        Описание: тестирование добавления пользователя с корректными данными.
        Ссылка: http://<APP_HOST>:<APP_PORT>/api/add_user
        Метод: POST
        Шаги:
            1) Создание пользователя;
            2) Получение из БДБ созданного пользователя.
        Проверки:
            1) Статус код: 201;
            2) Сообщение о создании сущности: "User was added!".
        """
    )
    def test(self, add_user_response: requests.Response) -> None:
        self.do_asserts([(add_user_response.text, "User was added!", "Проверка сообщения о создании сущности"),
                         (add_user_response.status_code, 201, "Проверка статус кода")])


class TestOpenAPIClientAddUserNegative(PrepareOpenAPIClient):

    def get_response(self, user: dict) -> typing.Tuple[requests.Response, ModelTestUsers]:
        # Выполнение запроса на добавление пользователя.
        r = self.execute_http_query(self.open_api_client.post_add_user, raise_exception=False, **user)

        # Получение модели пользователя из БД.
        m = self.orm_client.session.query(ModelTestUsers).filter_by(username=user['username']).all()
        self.orm_client.session.commit()

        return r, m

    @pytest.mark.API
    @pytest.mark.API_BACKEND
    @allure.epic("API Testing")
    @allure.feature("API Open")
    @allure.story("Incorrect user addition")
    @allure.description(
        """
        Описание: тестирование добавления пользователя ошибочными данными.
        Ссылка: http://<APP_HOST>:<APP_PORT>/api/add_user
        Метод: POST
        Шаги:
            1) Создание пользователя;
            2) Получения данных из БД;
        Проверки:
            1) Статус код: 400;
            2) Сообщение о создании сущности: "User not added!".
            3) Пользователь не создан в БД.
        """
    )
    @pytest.mark.parametrize(
        "user",
        [
            Builder.user_data_for_open_api(username_length=5),
            Builder.user_data_for_open_api(username_length=17),
            Builder.user_data_for_open_api(validate_email=False),
            Builder.user_data_for_open_api(email_length=65),
            Builder.user_data_for_open_api(password_length=5),
            Builder.user_data_for_open_api(password_length=256)
        ],
        ids=[
            'Username length is 5',
            'Username length is 17',
            'Incorrect email',
            'Email length is 65',
            'Password length is 5',
            'Password length is 256'
        ]
    )
    def test_add_user_negative(self, user: dict) -> None:
        resp = self.get_response(user)
        self.do_asserts([(resp[0].status_code, 400, "Проверка статус кода"),
                         (resp[0].text, "User not added!", "Проверка сообщения о создании сущности"),
                         (len(resp[1]), 0, "Пользователь не в БД")])

    @pytest.mark.API
    @pytest.mark.API_BACKEND
    @allure.epic("API Testing")
    @allure.feature("API Open")
    @allure.story("Incorrect user addition")
    @allure.description(
        """
        Описание: тестирование ранее созданного пользователя.
        Ссылка: http://<APP_HOST>:<APP_PORT>/add_user
        Шаги:
            1) Создаётся тестовый пользователя;
            2) Попытка создания нового пользователя с такими же данными.
        Проверки:
            1) Статус код: 304;
            2) Сообщение о создании сущности: "".
        """
    )
    @pytest.mark.parametrize("user", [Builder.user_data_for_open_api()], ids=["Correct credentials"])
    def test_add_exists_user_negative(self, user: dict) -> None:
        resp = self.get_response(user)
        self.do_asserts([(resp[0].status_code, 304, "Проверка статус кода"),
                         (resp[0].text, "", "Проверка сообщения о создании сущности"),
                         (len(resp[1]), 0, "Проверка создания пользователя")])


class TestOpenAPIClientAddUserForNotAuthorization(PrepareOpenAPIClient):
    CREATE_USER: bool = False

    @pytest.mark.API
    @pytest.mark.API_BACKEND
    @allure.epic("API Testing")
    @allure.feature("API Open")
    @allure.story("Incorrect user addition")
    @allure.description(
        """
        Описание: тестирование добавления пользователя без авторизации.
        Ссылка: http://<APP_HOST>:<APP_PORT>/api/add_user
        Метод: POST
        Шаги:
            1) Выполнение запроса.
        Проверки:
            1) Статус код: 401;
            2) Сообщение о создании сущности: "session lifetime expires".
            3) Проверка url запроса.
        """
    )
    @pytest.mark.parametrize("user", [Builder.user_data_for_open_api()], ids=["Not authorization user"])
    def test_user_add_negative_for_not_authorization(self, user: dict) -> None:
        self.do_incorrect_query(self.open_api_client.post_add_user, 'add_user', **user)


class TestOpenAPIClientDeleteUserPositive(PrepareOpenAPIClient):

    def prepare_to_delete_user(self, user: dict) -> typing.Tuple[requests.Response, ModelTestUsers]:
        self.create_user(user)

        r = self.execute_http_query(self.open_api_client.get_delete_user,
                                    raise_exception=False,
                                    username=user['username'])

        user_from_db = self.orm_client.session.query(ModelTestUsers).filter_by(username=user['username']).all()
        self.orm_client.session.commit()
        return r, user_from_db

    @pytest.mark.API
    @pytest.mark.API_OPEN
    @allure.epic("API Testing")
    @allure.feature("API Open")
    @allure.story("Correct user deletion")
    @allure.description(
        """
        Описание: тестирование удаления пользователя при корректных данных.
        Ссылка: http://<APP_HOST>:<APP_PORT>/api/del_user
        Метод: GET
        Шаги:
            1) Создание пользователя;
            2) Удаление пользователя через запрос;
            3) Получение тестового пользователя из БД.
        Проверки:
            1) Статус код: 204;
            2) Сообщение о создании сущности: "".
            3) Проверка удаления пользователя в БД.
        """
    )
    @pytest.mark.parametrize("user", [Builder.user_data_for_open_api()], ids=['Correct credentials'])
    def test(self, user: dict) -> None:
        resp = self.prepare_to_delete_user(user)
        self.do_asserts([(resp[0].status_code, 204, "Удаление пользователя"),
                         (resp[0].text, "", "Проверка сообщения"),
                         (len(resp[1]), 0, "Проверка удаления пользователя")])


class TestOpenAPIClientDeleteUserForNotAuthorization(PrepareOpenAPIClient):
    CREATE_USER: bool = False

    @pytest.mark.API
    @pytest.mark.API_OPEN
    @allure.epic("API Testing")
    @allure.feature("API Open")
    @allure.story("Incorrect user deletion")
    @allure.description(
        """
        Описание: тестирование удаления пользователя без авторизации.
        Ссылка: http://<APP_HOST>:<APP_PORT>/api/del_user
        Метод: GET
        Шаги:
            1) Удаление пользователя через запрос;
            3) Получение тестового пользователя из БД.
        Проверки:
            1) Статус код: 401;
            2) Сообщение о создании сущности: "session lifetime expires".
            3) Проверка URL запроса.
        """
    )
    @pytest.mark.parametrize("user", [Builder.user_data_for_open_api()], ids=['Incorrect credentials'])
    def test(self, user: dict) -> None:
        self.do_incorrect_query(self.open_api_client.get_delete_user,
                                f'del_user/{user["username"]}',
                                username=user['username'])


class TestOpenAPIClientDeleteNotExistentUser(PrepareOpenAPIClient):

    @pytest.mark.API
    @pytest.mark.API_OPEN
    @allure.epic("API Testing")
    @allure.feature("API Open")
    @allure.story("Incorrect user deletion")
    @allure.description(
        """
        Описание: тестирование удаления несуществующего пользователяю.
        Ссылка: http://<APP_HOST>:<APP_PORT>/api/del_user
        Метод: GET
        Шаги:
            1) Удаление пользователя через запрос.
        Проверки:
            1) Статус код: 404;
            2) Сообщение о создании сущности: "User does not exist!".
        """
    )
    @pytest.mark.parametrize("user", [Builder.user_data_for_open_api()], ids=['Correct credentials'])
    def test_user_delete_not_existent_user(self, user: dict) -> None:
        resp = self.execute_http_query(self.open_api_client.get_delete_user,
                                       raise_exception=False,
                                       username=user['username'])

        self.do_asserts([(resp.status_code, 404, "Статус код"),
                         (resp.text, "User does not exist!", "Проверка сообщения")])


class TestOpenAPIClientBlockUserPositive(PrepareOpenAPIClient):

    def prepare_to_block(self, user: dict) -> typing.Tuple[requests.Response, ModelTestUsers]:
        self.create_user(user)

        r = self.execute_http_query(self.open_api_client.get_block_user,
                                    username=user['username'],
                                    raise_exception=False)
        m = self.orm_client.session.query(ModelTestUsers).filter_by(username=user['username']).one()
        self.orm_client.session.commit()
        return r, m

    @pytest.mark.API
    @pytest.mark.API_OPEN
    @allure.epic("API Testing")
    @allure.feature("API Open")
    @allure.story("Correct blocking of the user")
    @allure.description(
        """
        Описание: блокировка пользователя с корректными данными.
        Ссылка: http://<APP_HOST>:<APP_PORT>/api/block_user
        Метод: GET
        Шаги:
            1) Создание тестового пользователя;
            2) Выполнение запроса на блокировку.
        Проверки:
            1) Статус код: 200;
            2) Сообщение о создании сущности: "User was blocked!";
            3) Проверка блокировки в БД.
        """
    )
    @pytest.mark.parametrize("user", [Builder.user_data_for_open_api()], ids=['Correct credentials'])
    def test(self, user: dict) -> None:
        resp = self.prepare_to_block(user)
        self.do_asserts([(resp[0].status_code, 200, "Проверка статус кода"),
                         (resp[0].text, 'User was blocked!', "Проверка сообщения"),
                         (resp[1].access, 0, "Проверка блокировки в БД")])


class TestOpenAPIClientBlockUserNegative(PrepareOpenAPIClient):
    CREATE_USER: bool = False

    @pytest.mark.API
    @pytest.mark.API_OPEN
    @allure.epic("API Testing")
    @allure.feature("API Open")
    @allure.story("Incorrect blocking of the user")
    @allure.description(
        """
        Описание: блокировка пользователя при некорректных данных.
        Ссылка: http://<APP_HOST>:<APP_PORT>/api/block_user
        Метод: GET
        Шаги:
            1) Выполнение запроса на блокировку.
        Проверки:
            1) Статус код: 401;
            2) Сообщение о создании сущности: "session lifetime expires";
            3) Проврерка URL запроса.
        """
    )
    @pytest.mark.parametrize("user", [Builder.user_data_for_open_api()], ids=['Incorrect credentials'])
    def test(self, user: dict) -> None:
        self.do_incorrect_query(self.open_api_client.get_block_user,
                                f'block_user/{user["username"]}',
                                username=user['username'])


class TestOpenAPIClientBlockUserAndAuthPositive(PrepareOpenAPIClient):
    _response: requests.Response = None

    def prepare(self) -> None:
        # Создаём сервисного пользователя.
        super(TestOpenAPIClientBlockUserAndAuthPositive, self).prepare()

        # Создаём данные для пользователя.
        user = Builder.user_data_for_open_api()

        # Создаём заблокированного пользователя.
        self.mysql_builder.create_user(**user, access=0)

        # Выполняем запрос на разблокировку.
        self._response = self.backend_api_client.post_login(username=user['username'],
                                                            password=user['password'],
                                                            submit="Login",
                                                            raise_exception=False)

    @pytest.mark.API
    @pytest.mark.API_OPEN
    @allure.epic("API Testing")
    @allure.feature("API Open")
    @allure.story("Correct blocking of the user")
    @allure.description(
        """
        Описание: блокировка пользователя и попытка войти в систему.
        Ссылка: http://<APP_HOST>:<APP_PORT>/api/block_user
        Метод: GET
        Шаги:
            1) Выполнение запроса на блокировку;
            2) Попытка войти в систему.
        Проверки:
            1) Статус код: 401;
            2) Сообщение о создании сущности: "User was blocked!".
        """
    )
    @pytest.mark.parametrize("user", [Builder.user_data_for_open_api()], ids=['Correct credentials'])
    def test(self, user: dict) -> None:
        self.do_asserts([(self._response.status_code, 401, "Проверка статус кода"),
                         (self._response.text, 'User was blocked!', "Проверка сообщения")])


class TestOpenAPIClientAcceptUserPositive(PrepareOpenAPIClient):
    _response: requests.Response = None
    _model_from_db: ModelTestUsers = None

    def prepare(self) -> None:
        # Перевыполнение базового метода.
        super(TestOpenAPIClientAcceptUserPositive, self).prepare()

        # Создание модели пользователя.
        user = Builder.user_data()

        # Создаём пользователя через БД.
        self.mysql_builder.create_user(username=user['username'], password=user['password'],
                                       email=user['email'], access=0)

        # Выполняем запрос на создание пользователя.
        self._response = self.execute_http_query(self.open_api_client.get_accept_user,
                                                 username=user['username'],
                                                 raise_exception=False)

        # Получаем модель из базы данных.
        self._model_from_db = self.orm_client.session.query(ModelTestUsers).filter_by(username=user['username']).one()
        self.orm_client.session.commit()

    @pytest.mark.API
    @pytest.mark.API_OPEN
    @allure.epic("API Testing")
    @allure.feature("API Open")
    @allure.story("Correct access of the user")
    @allure.description(
        """
        Описание: разблокировка пользователя с корректными данными.
        Ссылка: http://<APP_HOST>:<APP_PORT>/api/accept_user
        Метод: GET
        Шаги:
            1) Выполнение запроса на блокировку;
            2) Разблокировка пользователя;
            3) Получение данных из БД.
        Проверки:
            1) Статус код: 200;
            2) Сообщение о создании сущности: "User access granted!";
            3) Проверка разблокировки в БД.
        """
    )
    def test(self) -> None:
        self.do_asserts([(self._response.status_code, 200, "Проверка статус кода"),
                         (self._response.text, 'User access granted!', "Проверка сообщения"),
                         (self._model_from_db.access, 1, "Проверка разблокировки в БД")])


class TestOpenAPIClientAcceptUserNegative(PrepareOpenAPIClient):
    CREATE_USER: bool = False

    @pytest.mark.API
    @pytest.mark.API_OPEN
    @allure.epic("API Testing")
    @allure.feature("API Open")
    @allure.story("Incorrect access of the user")
    @allure.description(
        """
        Описание: разблокировка пользователя с некорректными данными.
        Ссылка: http://<APP_HOST>:<APP_PORT>/api/accept_user
        Метод: GET
        Шаги:
            1) Выполнение запроса на блокировку.
        Проверки:
            1) Статус код: 401;
            2) Сообщение о создании сущности: "session lifetime expires";
            3) Проверка URL запроса.
        """
    )
    @pytest.mark.parametrize("user", [Builder.user_data_for_open_api()], ids=['Correct credentials'])
    def test(self, user: dict) -> None:
        self.do_incorrect_query(self.open_api_client.get_accept_user,
                                f'accept_user/{user["username"]}',
                                username=user['username'])
