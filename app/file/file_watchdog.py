from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from pathlib import Path
from app.file import HostFile
from app.lookup import find_all_ip_hostname
from app.logger import get_logger
from app.utils import add_new_ip_all_service, delete_host_from_all_service


log = get_logger(__name__)


class HostFileWatchdog:
    """Класс для работы со слежением за файлом с хостами"""
    def __init__(self, file_path: [Path, str]):
        self.file_path = Path(file_path)
        self.observer = Observer()

        # Если файла с хостами не существует - создать его
        if not self.file_path.exists():
            log.warning(f"По адресу {self.file_path} не обнаружен файл, будет создан новый")
            try:
                self.file_path.touch()
            except OSError as err:
                log.error(f"Ошибка при создании файла: {err}")

        hostname_handler = self.HostFileHandler(
            patterns=[self.file_path.parts[-1]],
            ignore_directories=True,
            case_sensitive=False)
        file_dir = '/'.join(self.file_path.parts[:-1]).replace("\\", '') if len(self.file_path.parts) > 1 else "./"
        self.observer.schedule(hostname_handler, path=file_dir)

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
            host_file = HostFile(host_file_path=file_path)
            new_hosts = host_file.find_new_host()
            if new_hosts:
                log.info(f"Обнаружено добавление хостов: {', '.join(new_hosts)}")
                for host in new_hosts:
                    ip_list = find_all_ip_hostname(hostname=host)
                    add_new_ip_all_service(hostname=host, ip_address_list=ip_list)

            deleted_hosts = host_file.find_deleted_host()
            if deleted_hosts:
                log.info(f"Обнаружено удаление хостов: {', '.join([host.hostname for host in deleted_hosts])}")
                for host in deleted_hosts:
                    delete_host_from_all_service(hostname=host)

    async def start(self) -> None:
        """
        Запускает слежение за файлом
        Returns:
            None:
        """
        self.observer.start()
        log.info(f"Запущено слежение за файлом {self.file_path}")
