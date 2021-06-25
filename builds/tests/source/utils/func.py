import os
import logging


def rm_tree(file_path: str) -> None:
    files = os.listdir(file_path)

    for file in files:
        path = os.path.join(file_path, file)

        if os.path.isdir(path):
            rm_tree(path)
            os.rmdir(path)
        else:
            os.remove(path)


def create_logger(test_dir: str, file_name: str, logger_name: str, debugging: bool = False) -> logging.Logger:
    log_formatter = logging.Formatter('%(asctime)s - %(filename)-15s - %(levelname)-6s - %(message)s')
    log_file = os.path.join(test_dir, file_name)
    log_level = logging.DEBUG if debugging else logging.INFO

    file_handler = logging.FileHandler(log_file, 'w')
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(log_level)

    log = logging.getLogger(logger_name)
    log.propagate = False
    log.setLevel(log_level)
    log.handlers.clear()
    log.addHandler(file_handler)

    return log
