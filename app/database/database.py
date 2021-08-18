from peewee import SqliteDatabase
from .exceptions import *
from .models import *
from app.logger import get_logger


log = get_logger(__name__)


class Database:
    """Класс для работы с БД SQLite"""

    def __init__(self, database: str):
        self.db = SqliteDatabase(database=database, pragmas={'foreign_keys': 1})
        self.models = [Host, IpAddress]

    def start(self) -> bool:
        """
        Создает подключение к БД, если не удается, то выводит ошибку о невозможности подключения

        Returns:
            bool: Состояние подключения к БД
        """
        try:
            self.db.connect()
            log.info(f"Подключение к базе данных {self.db.database} успешно")
            return True
        except OperationalError as dbErr:
            log.error(dbErr)
            return False

    def drop_all(self) -> None:
        """
        Удаляет все таблицы в базе данных

        Returns:
            None:
        """
        self.db.drop_tables(self.models)

    @classmethod
    def drop_current(cls, model: BaseModel) -> None:
        """
        Удаляет определенную модель базы данных

        Args:
            model (BaseModel): Модель, которую необходимо удалить из БД

        Returns:
            None:
        """

        model.drop_table()

    @classmethod
    def _check_missing_tables(cls, tables: list) -> list:
        """
        Проверяет недостающие таблицы, если такие есть, возвращает список недостающих моделей

        Args:
            tables(list): список моделей, которые необходимо проверить

        Returns:
            list: Вернет список недостающих моделей
        """
        missing_tables = [table for table in tables if not table.table_exists()]
        return missing_tables if missing_tables else False

    def _init_tables(self) -> None:
        """
        Инизиализирует таблицы БД

        Returns:
            None:
        """
        missing_tables = self._check_missing_tables(self.models)

        if missing_tables:
            log.info(f"Создание недостающих таблиц: {', '.join([table.__name__ for table in missing_tables])}")

            try:
                self.db.create_tables(missing_tables)
                log.info("Таблицы успешно созданы")
            except OperationalError as dbErr:
                log.critical(dbErr)

        else:
            log.info("Таблицы базы данных в порядке")

    def init(self) -> bool:
        """
        Инициализирует базу данных

        Returns:
            bool: True - БД прошла инициализацию, False - не прошла
        """
        if self.start():
            self._init_tables()
            return True
        else:
            return False

    @classmethod
    def add_new_host(cls, hostname: str) -> Host:
        """
        Создает новую запись с хостом
        Args:
            hostname (str): Название хоста

        Returns:
            app.database.models.Host: Вернет модель Host, если создана новая строка в таблице

        Raises:
            IntegrityError: Возникнет ошибка, если добавляемый хост уже существует в базе данных
        """
        try:
            host_model = Host.create(hostname=hostname)
            return host_model

        except IntegrityError:
            raise IntegrityError("Данный хост уже существует в базе данных")

    @staticmethod
    def check_ip_unique(hostname: Host, ip_check: str) -> bool:
        """
        Проверяет на уникальность IP в записях к данном хосту
        Args:
            hostname (app.database.models.Host): Модель хоста, для которого необходимо проверсти проверку
            ip_check (str): Ip адрес для проверки

        Returns:
            bool: True - если IP уникальный, False - если уже записан в базе данных к данному хосту
        """
        return True if IpAddress.get_or_none(IpAddress.hostname_id == hostname.id,
                                             IpAddress.ip_address == ip_check) is None else False

    @classmethod
    def add_host_ip(cls, hostname: Host, ip_address: str) -> IpAddress:
        """
        Добавляет IP со связью к хосту
        Args:
            hostname (app.database.models.Host): Модель хоста, к которому необходимо добавитиь IP
            ip_address (str): IP-адрес для добавления

        Returns:
            app.database.models.IpAddress: Добавленный IpAddress
        """
        if cls.check_ip_unique(hostname=hostname, ip_check=ip_address):
            ip_address_model = IpAddress.create(hostname_id=hostname.id, ip_address=ip_address)
            log.info(f"[{hostname.hostname}] Добавлен IP: {ip_address}")
            return ip_address_model

    @classmethod
    def add_host_ip_list(cls, hostname: Host, ip_list: list) -> list:
        """
        Добавляет список IP со связью к хосту
        Args:
            hostname (app.database.models.Host): Модель хоста, к которому необходимо добавитиь IP
            ip_list (list): Список IP-адресов для добавления

        Returns:
            list: Список добавленных IpAddress
        """
        # Добавляет все ip из списка с привязкой к указанному хосту
        ip_address_models = [ip for ip in [
            cls.add_host_ip(hostname=hostname, ip_address=ip_address) for ip_address in ip_list] if ip is not None]

        return ip_address_models

    @classmethod
    def get_host_list(cls) -> list:
        """
        Получить список названий хостов из базы данных

        Returns:
            list: Список названий хостов
        """
        return [host for host in Host.select()]

    @classmethod
    def get_or_create_host_by_name(cls, hostname: str) -> Host:
        """
        Получить модель хоста в базе данных, если не существует - создать новую и вернуть её модель
        Args:
            hostname (str): Название хоста
        Returns:
            app.database.models.Host: Модель хоста
        """
        return Host.get_or_create(hostname=hostname)[0]

    @classmethod
    def get_host_ip_list(cls, hostname: Host) -> list:
        """
        Получить список ip, привязанных к хосту
        Args:
            hostname (app.database.models.Host): Модель хоста, у которого необходимо найти все IP

        Returns:
            list: Список IP адресов, связанных с указанным хостом
        """
        return [ip.ip_address for ip in IpAddress.select().where(IpAddress.hostname_id == hostname.id)]

    @classmethod
    def delete_ip_by_hostname(cls, hostname: Host, ip_address: str) -> None:
        """
        Удалить из таблицы определенный ip по id хоста
        Args:
            hostname (app.database.models.Host): Модель хоста, из которого необходимо убрать IP
            ip_address (str): IP Адрес, который необходимо удалить

        Returns:
            None:

        Raises:
            DoesNotExist: При попытке удалить по несуществующему ID
        """
        try:
            IpAddress.get(IpAddress.hostname_id == hostname.id, IpAddress.ip_address == ip_address).delete_instance()
            log.info(f"[{hostname.hostname}] Удален IP: {ip_address}")
        except DoesNotExist:
            raise DoesNotExist(f"IP {ip_address} - не записан в бд")

    @classmethod
    def delete_host_ip_list(cls, hostname: Host, ip_list: list) -> None:
        """
        Удаляет список IP по id хоста
        Args:
            hostname (app.database.models.Host): Модель хоста, из которого необходимо убрать IP
            ip_list (list): Список IP-адресов для удаления

        Returns:
            None:
        """
        # Добавляет все ip из списка с привязкой к указанному хосту
        for ip_address in ip_list:
            cls.delete_ip_by_hostname(hostname=hostname, ip_address=ip_address)

    @classmethod
    def delete_hostname(cls, hostname: Host) -> None:
        """
        Удалить определенный хост и все его записи IP по id
        Args:
            hostname (app.database.models.Host): Модель хоста, который необходимо удалить

        Returns:
            None:

        Raises:
            DoesNotExist: При попытке удалить хоста по несуществущему ID
        """
        try:
            hostname.delete_instance()
            log.info(f"Хост {hostname.hostname} удален со всеми связанными IP")
        except DoesNotExist:
            raise DoesNotExist(f"Хоста не существует")

    @classmethod
    def get_all_host_with_ip(cls) -> dict:
        """
        Получить словарь хостов со всеми связанными IP
        Returns:

        """
        dict_host = {host.hostname: cls.get_host_ip_list(host) for host in cls.get_host_list()}

        return dict_host

    @classmethod
    def get_all_ip_address(cls) -> list:
        """
        Получить все записи IP
        Returns:
            list: Список со списком IP-адресов
        """
        ip_list = [ip for ip in IpAddress.select()]

        return ip_list
