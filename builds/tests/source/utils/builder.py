import logging

from faker import Faker

from orm.common.orm_client import ORMClient
from orm.models.MYSQL_DB import ModelTestUsers

_fake = Faker()


class Builder(object):

    @staticmethod
    def user_data(
            confirm_user_password: bool = True,
            validate_email: bool = True,
            username_length: int = 8,
            email_length: int = 12,
            password_length: int = 8,
            default_username: str = None,
            default_email: str = None,
            default_password: str = None
    ) -> dict:
        if default_username is None:
            username = _fake.lexify(''.join(['?' for _ in list(range(username_length))]))
        else:
            username = default_username

        if default_email is None:
            if validate_email:
                email = _fake.lexify(f"{''.join(['?' for _ in list(range(email_length - 6))])}@ex.ru")
            else:
                email = _fake.lexify(''.join(['?' for _ in list(range(email_length))]))
        else:
            email = default_email

        if default_password is None:
            password = _fake.lexify(''.join(['?' for _ in list(range(password_length))]))
            confirm = password if confirm_user_password else _fake.lexify(
                ''.join(['?' for _ in list(range(password_length))]))
        else:
            password = default_password
            confirm = default_password

        return {
            'username': username,
            'email': email,
            'password': password,
            'confirm': confirm
        }

    @staticmethod
    def user_data_for_open_api(
            validate_email: bool = True,
            username_length: int = 8,
            email_length: int = 12,
            password_length: int = 8,
            default_username: str = None,
            default_email: str = None,
            default_password: str = None
    ):
        user = Builder.user_data(validate_email=validate_email, username_length=username_length,
                                 email_length=email_length, password_length=password_length,
                                 default_email=default_email, default_username=default_username,
                                 default_password=default_password)

        return {
            'username': user['username'],
            'email': user['email'],
            'password': user['password']
        }


class MySQLBuilder(object):
    client: ORMClient = None

    def __init__(self, client: ORMClient) -> None:
        self.client = client

    def create_user(self, username: str, password: str, email: str, access: int = 1, active: int = 0) -> ModelTestUsers:
        # Создание модели пользователя.
        model = ModelTestUsers(username=username,
                               password=password,
                               email=email,
                               access=access,
                               active=active)

        # Логирование созданного пользователя в БД.
        logging.getLogger('mysql-logger').info(f"- Добавление пользователя: {model}")

        # Добавление пользователя в БД.
        self.client.session.add(model)
        self.client.session.commit()
        return model
