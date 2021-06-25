import typing

from selenium.webdriver.common.by import By

TLocatorElement = typing.Tuple[str, str]


class _CPLocators(object):
    INPUT_USERNAME: TLocatorElement = (By.ID, 'username')
    INPUT_PASSWORD: TLocatorElement = (By.ID, 'password')

    BUTTON_SUBMIT: TLocatorElement = (By.ID, 'submit')
    BUTTON_REGISTRATION: TLocatorElement = (By.XPATH, '/html/body/div/div/div/div/div/form/div[4]/a')

    LABEL_MESSAGE: TLocatorElement = (By.ID, 'flash')


class LoginPageLocators(_CPLocators):
    pass


class RegistrationPageLocators(_CPLocators):
    INPUT_EMAIL: TLocatorElement = (By.ID, 'email')
    INPUT_CONFIRM_PASSWORD: TLocatorElement = (By.ID, 'confirm')
    INPUT_TERM: TLocatorElement = (By.ID, 'term')
