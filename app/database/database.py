from peewee import SqliteDatabase, OperationalError
from app.utils.fpylog import Log
from .exceptions import *
from .models import *

log = Log(file_log=True, file_log_name='db')


class Database:
    """Класс для работы с БД SQLite"""

    def __init__(self, database: str):
        self.db = SqliteDatabase(database=database)
        self.models = [Host, IpAddress]

    def start(self) -> bool:
        """
        Создает подключение к БД, если не удается, то выводит ошибку о невозможности подключения
        Returns:
            bool: Состояние подключения к БД
        """
        try:
            self.db.connect()
            log.success(f"Подключение к бд успешно", log_file=False)
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
            log.warn(f"Создание недостающих таблиц:")
            for table in missing_tables:
                print(table.__name__)

            try:
                self.db.create_tables(missing_tables)
                log.success("Таблицы успешно созданы")
            except OperationalError as dbErr:
                log.error(dbErr)

        else:
            log.success("Таблицы БД в порядке", log_file=False)

    async def init(self) -> bool:
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
            Host: Вернет модель Host, если создана новая строка в таблице

        Raises:
            IntegrityError: Возникнет ошибка, если добавляемый хост уже существует в базе данных
        """
        try:
            video_server_model = Host.create(hostname=hostname)
            return video_server_model

        except peewee.IntegrityError:
            raise IntegrityError("Данный хост уже существует в базе данных")

    @classmethod
    def add_host_ip(cls, hostname: str, ip_address: str) -> IpAddress:
        """
        Добавляет IP со связью к хосту
        Args:
            hostname (str):
            ip_address (str):

        Returns:
            list: Список добавленных IpAddress
        Raises:
        """

        # Так как get_or_create возвращает Tuple, обращаюсь к ID по индексу
        hostname_id = Host.get_or_create(hostname=hostname)[0]
        ip_address_model = IpAddress.create(hostname_id=hostname_id, ip_address=ip_address)

        return ip_address_model

    @classmethod
    def add_host_ip_list(cls, hostname: str, ip_list: list) -> list:
        """
        Добавляет список IP со связью к хосту
        Args:
            hostname (str):
            ip_list (list):

        Returns:
            list: Список добавленных IpAddress
        Raises:
        """

        ip_address_models = [cls.add_host_ip(hostname=hostname, ip_address=ip_address) for ip_address in ip_list]

        return ip_address_models
