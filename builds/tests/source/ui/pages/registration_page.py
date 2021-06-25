import os

from ui.pages.base_page import BasePageActions
from ui.locators.locators import RegistrationPageLocators
from ui.pages.main_page import MainPage


class RegistrationPage(BasePageActions):
    url: str = f'http://{os.environ["APP_HOST"]}:{os.environ["APP_PORT"]}/reg'
    locators = RegistrationPageLocators()

    def registration(self, username: str, email: str, password: str, confirm: str, term: str = 'y') -> MainPage:
        """
        Регистрация пользователя в системе.
        :param username: имя пользователя.
        :param email: электронная почта пользователя.
        :param password: пароль пользователя.
        :param confirm: подтверждение пароля пользователя.
        :param term: подтверждение регистрации.
        :return: None.
        """
        # Включаем ожидание
        self.wait_by_time(3.0)

        # Вводим данные для регистрации.
        self.send_keys(self.locators.INPUT_USERNAME, username)
        self.send_keys(self.locators.INPUT_EMAIL, email)
        self.send_keys(self.locators.INPUT_PASSWORD, password)
        self.send_keys(self.locators.INPUT_CONFIRM_PASSWORD, confirm)

        if term == "y":
            self.click(self.locators.INPUT_TERM)

        # Регистрируемся.
        self.click(self.locators.BUTTON_SUBMIT)

        return MainPage(driver=self.driver,
                        page_configuration=self.configuration)

    def get_error_msg(self) -> str:
        """
        Получить сообщение об ошибке.
        :return: str - сообщение.
        """
        return self.get_text_from_obj(self.locators.LABEL_MESSAGE)
