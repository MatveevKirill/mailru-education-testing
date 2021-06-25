import pytest
from _pytest.fixtures import FixtureRequest

from utils.builder import Builder


@pytest.fixture(scope="function",
                params=[{},
                        {'username_length': 6},
                        {'username_length': 16},
                        {'email_length': 64},
                        {'password_length': 6},
                        {'password_length': 255}],
                ids=["Correct credentials",
                     'Username length is 6',
                     'Username length is 16',
                     'Email length is 64',
                     'Password length is 6',
                     'Password length is 255'])
def user_positive(request: FixtureRequest) -> dict:
    return Builder.user_data(**request.param)


@pytest.fixture(scope="function",
                params=[{'username_length': 5},
                        {'username_length': 17},
                        {'default_email': ''},
                        {'email_length': 65},
                        {'validate_email': False},
                        {'password_length': 5},
                        {'password_length': 256}],
                ids=["Username length is 6",
                     "Username length is 17",
                     "Email length is 0",
                     "Email length is 65",
                     "Incorrect email format",
                     "Password length is 5",
                     "Password length is 256"])
def user_negative(request: FixtureRequest) -> dict:
    return Builder.user_data(**request.param)


@pytest.fixture(scope="function",
                params=[{'default_username': "''' \"\" ;;; SELECT * FROM test_users; /*@mail.ru"},
                        {'default_username': "<b>XSS!</b>"}],
                ids=["Base SQL-injection attack",
                     "Base XSS attack"])
def negative_attack_user(request: FixtureRequest) -> dict:
    return Builder.user_data(**request.param)
