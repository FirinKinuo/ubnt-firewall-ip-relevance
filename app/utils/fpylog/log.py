from datetime import datetime
from pathlib import Path
from os import environ


def _prepare_log(log_type: str, message: []) -> str:
    log_types = {
        'warn': "\033[33mWARN",
        'error': "\033[31mERR",
        'info': "\033[35mINFO",
        'success': "\033[36mSUCC",
    }
    return f"\033[38m{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} | {log_types[log_type]} > \033[37m{message}"


def log_warn(message: []) -> None:
    print(_prepare_log(log_type='warn', message=message))


def log_error(message: []) -> None:
    print(_prepare_log(log_type='error', message=message))


def log_info(message: []) -> None:
    print(_prepare_log(log_type='info', message=message))


def log_success(message: []) -> None:
    print(_prepare_log(log_type='success', message=message))


class Log:
    def __init__(self, file_log=False, file_log_name="log", file_log_path=""):
        self.file_log = file_log
        self.file_log_name = file_log_name
        self.file_log_path = Path(environ.get('LOG_PATH'), file_log_path)

    def _log_in_file(self, type_log: str, message: []) -> None:
        if self.file_log:
            with open(Path(self.file_log_path, (self.file_log_name + '.log')), 'a', encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} | {type_log} > {message}\n")

    def warn(self, message: [], log_file: bool = True) -> None:
        log_warn(message=message)
        if log_file:
            self._log_in_file("WARNING", message)

    def error(self, message: [], log_file: bool = True) -> None:
        log_error(message=message)
        if log_file:
            self._log_in_file("ERROR", message)

    def info(self, message: [], log_file: bool = True) -> None:
        log_info(message=message)
        if log_file:
            self._log_in_file("INFO", message)

    def success(self, message: [], log_file: bool = True) -> None:
        log_success(message=message)
        if log_file:
            self._log_in_file("SUCCESS", message)
