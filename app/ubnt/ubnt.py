from Exscript.protocols import SSH2
from Exscript.protocols.exception import InvalidCommandException
from Exscript.key import PrivateKey
from Exscript import Account
from pathlib import Path
import re

from app.ubnt.exceptions import *
from app.logger import get_logger

log = get_logger(__name__)


class UbntService:
    def __init__(self, host: str, login: str, firewall_group: str, password: str = '', port: int = 22,
                 key: [str, Path, None] = None):
        """
        Args:
            host (str): Хост для подключения к роутеру
            login (str): Логин для подключения к роутеру
            password (str): Пароль для подключения к роутеру
            port (int): Порт для подключения к роутеру
            key (str|Path|None): Путь до приватного ключа для подключения к роутеру
            firewall_group (str): Название группы ip-адресов для firewall
        """
        self.host = host
        self.login = login
        self.password = password
        self.port = port
        self.key = PrivateKey().from_file(key) if key is not None else key
        self.ssh = SSH2()
        self.firewall_group = firewall_group

    def __ssh_connect(self):
        """Открыть соединение по SSH"""
        self.ssh.connect(hostname=self.host, port=self.port)
        self.ssh.login(Account(name=self.login, password=self.password, key=self.key))
        log.info(f"Подключенно по ssh к {self.login}@{self.host}:{self.port}")

    def _configure_mode(self) -> None:
        """
        Переход в режим конфигурации ubnt
        Returns:
            None:
        """
        try:
            self.ssh.execute("configure")
        except InvalidCommandException as err:
            # Если не находит команду configure, то скорее всего подключение уже в режиме configure
            if 'configure: command not found' in err.args[0]:
                self.ssh.execute("discard")
            else:
                raise InvalidCommandException(err)

    def _ip_group_action(self, ip_address_list: list, group_name: str, action: str):
        """
            Производит указанное действие в группе IP адресов
            Args:
                ip_address_list (list): Список ip адресов для firewall
                group_name (str): Название группы, где необходимо провести действие
                action(str):
                            add - Добавить список IP в группу,
                            delete - Удалить список IP из группы
            Returns:
                None:

            Raises:
                KeyError: Если переданный action не является допустимым
            """
        possible_actions = ('set', 'delete',)

        if action not in possible_actions:
            raise KeyError(f"Действие {action} - недопустимо")
        try:
            if not self.ssh.is_app_authorized():
                self.__ssh_connect()

            self._configure_mode()

            for ip in ip_address_list:
                if re.match((r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.' * 4)[:-2], ip) is not None:
                    self.ssh.execute(f"{action} firewall group address-group {group_name} address {ip}")

            self.ssh.execute("commit; save")
            self.ssh.execute("exit")

            log.info(f"{'Добавлены' if action == 'set' else 'Удалены'} "
                     f"IP: {', '.join(ip_address_list)} для группы {group_name}")

        except SSHTimeoutError as err:
            log.error(f"Ошибка SSH: {err}")

    def add_new_ip(self, ip_address_list: list) -> None:
        """
        Добавляет IP адреса в группу для Firewall
        Args:
            ip_address_list (list): Список ip адресов для добавления в firewall
        Returns:
            None:
        """
        self._ip_group_action(ip_address_list=ip_address_list, group_name=self.firewall_group, action='set')

    def delete_ip(self, ip_address_list: list) -> None:
        """
        Удаляет IP адреса из группы для Firewall
        Args:
            ip_address_list (list): Список ip адресов для удаления из firewall
        Returns:
            None:
        """
        self._ip_group_action(ip_address_list=ip_address_list, group_name=self.firewall_group, action='delete')

    def _force_close_configure_mode(self) -> None:
        """
        Гарантировано выйти из режима конфигурации
        Returns:
            None:
        """
        try:
            self.ssh.execute("configure")
        except InvalidCommandException:
            pass
        finally:
            self.ssh.execute("exit discard")

    def get_group_ip_list(self, group_name: str) -> list:
        """
        Получить список IP, записанных в группе
        Args:
            group_name (str): Название группы, из которой необходимо получить IP-адреса

        Returns:
            list: Список IP адресов
        """
        try:
            if not self.ssh.is_app_authorized():
                self.__ssh_connect()

            self._force_close_configure_mode()
            self.ssh.response = str()  # Очищаем последний response
            self.ssh.execute(f"show firewall group {group_name} | no-more")
            # Получаем ответ от ввода команды show, разделяем строки по разделителю \r\n, удаляем все пробелы
            # Ищем строки, что подходят по регулярке, как IP-адрес
            ip_list = [ip for ip in
                       map(lambda res_string: re.sub(r"\s+", '', res_string), self.ssh.response.split("\r\n"))
                       if re.match((r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.' * 4)[:-2], ip) is not None]
            return ip_list

        except SSHTimeoutError as err:
            log.error(f"Ошибка SSH: {err}")

