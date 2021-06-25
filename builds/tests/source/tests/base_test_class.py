import allure


class BaseTestClass(object):

    def prepare(self) -> None:
        pass

    @staticmethod
    def do_asserts(arr: list) -> None:
        errors = []
        for e in arr:
            try:
                with allure.step(e[2]):
                    assert e[0] == e[1], f"Not equal: '{e[0]}' != '{e[1]}'"
            except AssertionError as e:
                errors.append(e.args[0])

        if errors:
            raise AssertionError('\n'.join(errors))