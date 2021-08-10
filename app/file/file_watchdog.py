from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from pathlib import Path
from app.file import HostFile
from app.database import Database
from app.lookup import find_all_ip_hostname
from os import environ


class HostFileWatchdog:
    """Класс для работы со слежением за файлом с хостами"""

    def __init__(self, file_path: [Path, str]):
        self.file_path = Path(file_path)
        self.observer = Observer()

        hostname_handler = self.HostFileHandler(
            patterns=[self.file_path.parts[-1]],
            ignore_directories=True,
            case_sensitive=False)
        print('/'.join(self.file_path.parts[:-1]).replace("\\", ''))
        self.observer.schedule(hostname_handler, path='/'.join(self.file_path.parts[:-1]).replace("\\", ''))

    class HostFileHandler(PatternMatchingEventHandler):
        """Класс слежения за изменениями в файле"""

        def on_modified(self, event):
            """Обрабатывает ивенты при изменениях в файле"""
            self.update_ip_table(event.src_path)

        @classmethod
        def update_ip_table(cls, file_path: str) -> None:
            """
            Обновить данные в ip таблицах, если найдены изменения
            Args:
                file_path (str): Путь до файла с хостами

            Returns:
                None:
            """
            db = Database(database=environ.get("SQLITE_PATH"))
            host_file = HostFile(host_file_path=file_path)
            new_hosts = host_file.find_new_host()
            if new_hosts:
                for host in new_hosts:
                    ip_list = find_all_ip_hostname(hostname=host)
                    db.add_host_ip_list(hostname=host, ip_list=ip_list)

    async def start(self) -> None:
        """
        Запускает слежение за файлом
        Returns:
            None:
        """

        self.observer.start()
