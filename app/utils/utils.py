from asyncio import sleep as async_sleep
from app.setting import DATABASE, UBNT
from app.lookup import find_all_ip_hostname
from app.logger import get_logger


log = get_logger(__name__)


def add_new_ip_all_service(hostname: str, ip_address_list: list) -> None:
    """
        Утилита для добавления IP во всех сервисах, БД и Ubnt
    Args:
        hostname (str): Название хоста
        ip_address_list (list): Список IP адресов для добавления

    Returns:
        None:

    """
    hostname_model = DATABASE.get_or_create_host_by_name(hostname=hostname)
    DATABASE.add_host_ip_list(hostname=hostname_model, ip_list=ip_address_list)
    UBNT.add_new_ip(ip_address_list=ip_address_list)


def delete_ip_from_all_service(hostname: str, ip_address_list: list) -> None:
    """
        Утилита для удаления IP из всех сервисов, БД и Ubnt
    Args:
        hostname (str): Название хоста, откуда необходимо удалить IP
        ip_address_list (list): Список IP адресов для удаления

    Returns:
        None:
    """
    hostname_model = DATABASE.get_or_create_host_by_name(hostname=hostname)

    for ip in ip_address_list:
        DATABASE.delete_ip_by_hostname(hostname=hostname_model, ip_address=ip)

    UBNT.delete_ip(ip_address_list=ip_address_list)


def delete_host_from_all_service(hostname: str) -> None:
    """
        Утилита для удаления IP из всех сервисов, БД и Ubnt
    Args:
        hostname (app.database.models.Host): Модель, откуда необходимо удалить IP

    Returns:
        None:
    """
    ip_list = DATABASE.get_host_ip_list(hostname)
    DATABASE.delete_hostname(hostname=hostname)
    UBNT.delete_ip(ip_address_list=ip_list)


async def background_checking_relevance(hours: int = 3) -> None:
    """
    Проверять актуальность IP адресов всех записанных хостов через определенный промежуток
    Args:
        hours (int): Промежуток между проверками

    Returns:
        None:
    """
    while True:
        log.info("Проверка IP хостов в базе данных")
        host_list = DATABASE.get_all_host_with_ip()
        for host in host_list.keys():
            lookup_ip = find_all_ip_hostname(hostname=host, logging=False)
            db_host_ip = host_list[host]

            new_ip = set.difference(set(lookup_ip), set(db_host_ip))
            deleted_ip = set.difference(set(db_host_ip), set(lookup_ip))

            if new_ip:
                log.info(f"Для хоста {host} обнаружены новые IP: {', '.join(new_ip)}")
                add_new_ip_all_service(hostname=host, ip_address_list=list(new_ip))

            if deleted_ip:
                log.info(f"Для хоста {host} обнаружено удаление IP: {', '.join(new_ip)}")
                delete_ip_from_all_service(hostname=host, ip_address_list=list(deleted_ip))

        ubnt_ip = UBNT.get_group_ip_list(group_name=UBNT.firewall_group)
        if ubnt_ip is not None:
            log.info("Проверка IP записей в UBNT")

            db_ip_list = [ip.ip_address for ip in DATABASE.get_all_ip_address()]
            extra_ip = set.difference(set(ubnt_ip), set(db_ip_list))
            missing_ip = set.difference(set(db_ip_list), set(ubnt_ip))

            if extra_ip:
                log.info(f"Обнаружены неудаленные из UBNT IP: {', '.join(extra_ip)}")
                UBNT.delete_ip(ip_address_list=list(extra_ip))

            if missing_ip:
                log.info(f"Обнаружены недобавленные в UBNT IP: {', '.join(missing_ip)}")
                UBNT.add_new_ip(ip_address_list=list(missing_ip))

        log.info("Проверка успешно выполнена")
        await async_sleep(hours * 60)
