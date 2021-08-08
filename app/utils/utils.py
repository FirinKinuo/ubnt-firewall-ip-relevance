from pathlib import Path
from sys import path as sys_path
from dotenv import load_dotenv
from app.setting import DOT_ENV_PATH


def load_env_file() -> None:
    """
    Загружает данные из файла с виртуальным окружением, если данный файл невозможно прочитать, то скрипт завершается
    Returns:
        None:
    """
    load_dotenv(DOT_ENV_PATH)
