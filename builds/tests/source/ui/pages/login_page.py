import os

from ui.pages.base_page import BasePageActions
from ui.pages.registration_page import RegistrationPage
from ui.locators.locators import LoginPageLocators


class LoginPage(BasePageActions):
    url: str = f'http://{os.environ["APP_HOST"]}:{os.environ["APP_PORT"]}'
    locators: LoginPageLocators = LoginPageLocators()

    def login(self, username: str, password: str) -> None:
        """
        Авторизация на сервисе.
        :param username: имя пользователя;
        :param password: пароль пользователя.
        :return: None
        """
        # Вводим логин и пароль.
        self.send_keys(self.locators.INPUT_USERNAME, username)
        self.send_keys(self.locators.INPUT_PASSWORD, password)

        # Авторизуемся.
        self.click(self.locators.BUTTON_SUBMIT)

    def get_error_msg(self) -> str:
        """
        Получить сообщение об ошибке.
        :return: str - сообщение.
        """
        return self.get_text_from_obj(self.locators.LABEL_MESSAGE)

    def go_to_registration(self) -> RegistrationPage:
        """
        Переход на страницу регистрации.
        :return:
        """
        self.click(self.locators.BUTTON_REGISTRATION)
        return RegistrationPage(driver=self.driver,
                                page_configuration=self.configuration,
                                is_opened_params={'new_url': f'http://{os.environ["APP_HOST"]}:{os.environ["APP_PORT"]}/reg'})
