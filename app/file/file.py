from app.database import Database
from os import environ


class HostFile:
    """Класс для работы с файлом списка хостов"""
    def __init__(self, host_file_path: str):
        self.host_file_path = host_file_path

    def find_new_host(self) -> list:
        """
        Ищет обновления в файле
        Returns:
            list: Список добавленных хостов
        """

        db = Database(database=environ.get("SQLITE_PATH"))
        hostname_db = db.get_host_list()

        with open(self.host_file_path, 'r') as host_file:
            # Читаем список хостов из файла и разделяем их по символу переноса строки
            read_hosts = host_file.read().split("\n")
            # Отделяем хосты, которые занесены в БД
            return [host for host in read_hosts if host not in hostname_db]


