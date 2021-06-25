import logging
import time
import allure

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions

from ui import exceptions as ce
from ui.locators.locators import TLocatorElement
from utils.decorators import wait


class BasePageActions(object):
    url: str = None
    locators = None

    def __init__(self, driver: WebDriver, page_configuration: dict, is_opened_params: dict = None) -> None:
        """
        Инициализация базового класса для работы с элементами на странице.
        :param driver: драйвер Google Chrome.
        :param page_configuration: конфигурация тестирования UI.
        """
        self.driver = driver
        self.configuration = page_configuration
        self.is_opened(is_opened_params=is_opened_params)

        self.log(f"Go to {self.__class__.__name__}")

    @property
    def action_chains(self) -> ActionChains:
        return ActionChains(self.driver)

    @staticmethod
    def log(log: str, level: str = logging.INFO) -> None:
        """
        Запись в лог файл.
        :param log: лог.
        :param level: уровень лога.
        :return: None
        """
        logger = logging.getLogger('ui-logger')

        if level == logging.INFO:
            logger.info(log)
        elif level == logging.DEBUG:
            logging.debug(log)
        elif level == logging.WARNING:
            logging.warning(log)
        elif level == logging.ERROR:
            logging.warning(log)

    def wait_by_time(self, timeout: float) -> None:
        """
        Ожидание для страницы.
        :param timeout: время ожидания.
        :return: None
        """
        time.sleep(timeout)

    @allure.step("Нажать на элемент: {locator}")
    def click(self, locator: TLocatorElement) -> None:
        """
        Нажать на элемент на странице.
        :param locator: локатор элемента.
        :return: None.
        """

        def _click():
            self.action_chains.click(on_element=self.find_element(locator=locator)).perform()
            return

        return wait(
            _method=_click,
            _error=exceptions.StaleElementReferenceException,
            _timeout=self.configuration['timeout_limit']
        )

    @allure.step("Отправить данные в локатор: {locator}")
    def send_keys(self, locator: TLocatorElement, send_data: str, auto_clear: bool = True) -> None:
        """
            Отправить данные через ActionChains.send_keys.
            :param locator: локатор элемента.
            :param send_data: отправляемые данные.
            :param auto_clear: автоматическая очистка элемента перед отправкой. По умолчанию: True.
            :return: None
        """

        def _send_keys():
            element = self.find_element(locator=locator)
            if auto_clear:
                element.clear()
            return self.action_chains.send_keys_to_element(element, send_data).perform()

        return wait(
            _method=_send_keys,
            _error=exceptions.TimeoutException,
            _timeout=self.configuration['timeout_limit']
        )

    def scroll_to(self, locator: TLocatorElement) -> None:
        """
            Переместиться к элементу на странице.
            :param locator: локатор элемента.
            :return: None
        """

        def _scroll_to():
            return self.action_chains.move_to_element(
                to_element=(self.wait().until(EC.visibility_of_element_located(locator=locator)))
            )

        return wait(
            _method=_scroll_to,
            _error=exceptions.TimeoutException,
            _timeout=self.configuration['timeout_limit']
        )

    def wait(self, timeout: float = None) -> WebDriverWait:
        """
            Настройка ожиданий.
            :param timeout: время ожидания. По умолчанию: None.
            :return: WebDriverWait.
        """
        if timeout is None:
            timeout = self.configuration['timeout_limit']
        return WebDriverWait(self.driver, timeout=timeout)

    def find_element(self, locator: TLocatorElement, timeout: float = None) -> WebElement:
        """
            Найти элемент на странице.
            :param locator: локатор элемента.
            :param timeout: время для нахождения элемента.
            :return: WebElement
        """
        return self.wait(timeout=timeout).until(EC.presence_of_element_located(locator=locator))

    def get_text_from_obj(self, locator: TLocatorElement, timeout: float = None) -> str:
        """
            Получение текста из элемента страницы.
            :param locator: локатор элемента.
            :param timeout: время для нахождения элемента.
            :return: str
        """

        def _get_text_from_obj() -> str:
            return self.find_element(locator=locator, timeout=timeout).text

        return wait(
            _method=_get_text_from_obj,
            _error=exceptions.StaleElementReferenceException,
            _check=True,
            _timeout=self.configuration['timeout_limit']
        )

    def get_attr_from_obj(self, attribute_name: str, locator: TLocatorElement, timeout: float = None) -> str:
        """
            Получение атрибута из элемента.
            :param attribute_name: название атрибута.
            :param locator: локатор элемента.
            :param timeout: время для нахождения элемента.
            :return: str
        """

        def _get():
            return self.find_element(locator=locator, timeout=timeout).get_attribute(attribute_name)

        return wait(
            _method=_get,
            _error=exceptions.StaleElementReferenceException,
            _timeout=self.configuration['timeout_limit']
        )

    def get_selected_from_obj(self, locator: TLocatorElement, timeout: float = None) -> bool:
        """
            Получение значения True|False из is_selected элемента.
            :param locator: локатор элемента.
            :param timeout: время для нахождения элемента.
            :return: bool.
        """

        def _get_selected_from_obj():
            return self.find_element(locator=locator, timeout=timeout).is_selected()

        return wait(
            _method=_get_selected_from_obj,
            _error=exceptions.StaleElementReferenceException,
            _timeout=self.configuration['timeout_limit']
        )

    def refresh_page(self):
        """
            Обновить текущую страницу.
            :return: None
        """
        self.driver.refresh()

    def is_opened(self, is_opened_params: dict = None) -> bool:
        """
            Проверка на то, что страница загрузилась.
            :param is_opened_params: параметры для проверки страницы.
            :return: bool.
        """

        def _check_url() -> bool:
            """
            Проверка url драйвера и url PageObject`а.
            :return: Bool.
            """
            if is_opened_params is None:
                params = {
                    "ignore_get_params": False,
                    "new_url": None
                }
            else:
                params = is_opened_params

            current_url = self.driver.current_url.split("#")[0]

            if 'new_url' in params and params['new_url']:
                url = params['new_url']
            else:
                url = self.driver.current_url.split("#")[0]

            if 'ignore_get_params' in params and params['ignore_get_params']:
                current_url = current_url.split("?")[0]
                url = url.split("?")[0]

            if current_url != url:
                raise ce.PageNotLoadedException(
                    f"Page not loaded (current_url='{current_url}';url='{url}')"
                )
            return True

        return wait(
            _method=_check_url,
            _timeout=self.configuration['timeout_limit'],
            _error=ce.PageNotLoadedException,
            _check=True
        )

    def is_new_tab_panel(self, tab_id: int, is_new_page: bool = True) -> bool:
        """
            Сменить активное окно.
            :param tab_id: идентификатор окна.
            :param is_new_page: новое ли окно открывается при переходе.
            :return: bool.
        """
        pass
