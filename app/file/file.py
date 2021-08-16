from app.setting import DATABASE
import re


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

        hostname_db = DATABASE.get_host_list()

        with open(self.host_file_path, 'r') as host_file:
            # Читаем список хостов из файла и разделяем их по символу переноса строки
            read_hosts = host_file.read().split("\n")
            # Отделяем хосты, которые занесены в БД
            return [re.sub(r'(\s+)', '', host) for host in read_hosts if
                    host not in [host.hostname for host in hostname_db] and re.match(r".+\..+", host) is not None]

    def find_deleted_host(self) -> list:
        """
        Поиск хостов, что были удалены из файла
        Returns:
            list: Список хостов, которые были удалены
        """
        hostname_db = DATABASE.get_host_list()

        with open(self.host_file_path, 'r') as host_file:
            # Читаем список хостов из файла и разделяем их по символу переноса строки
            read_hosts = host_file.read().split("\n")
            # Ищем разницу между тем, что в файле и в базе данных
            return [host for host in hostname_db if host.hostname not in read_hosts]
