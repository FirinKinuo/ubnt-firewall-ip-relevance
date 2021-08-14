import logging
from os import environ

_log_format = f"%(asctime)s [%(levelname)s] - %(name)s | %(message)s"
_log_level = environ.get("LOGGING_LEVEL", "WARNING").upper()


def get_logger(name: str) -> logging.Logger:
    """
    Получить сконфигурированный логгер
    Args:
        name (str): Название модуля

    Returns:
        logging.Logger: Сконфигурированный экземпляр логгера
    """

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(_log_level)
    stream_handler.setFormatter(logging.Formatter(_log_format))

    file_handler = logging.FileHandler(
        filename=environ.get("LOGGING_PATH", 'ufir.log'),
        encoding='utf-8')
    file_handler.setLevel(_log_level)
    file_handler.setFormatter(logging.Formatter(_log_format))

    logger = logging.getLogger(name)
    logger.setLevel(_log_level)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger
