from asyncio import sleep as async_sleep
from app.setting import DATABASE, UBNT
from app.lookup import find_all_ip_hostname
from app.database.exceptions import DoesNotExist


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
    DATABASE.delete_ip_by_hostname(hostname=hostname_model, ip_address=ip_address_list)
    UBNT.delete_ip(ip_address_list=ip_address_list)


async def background_checking_relevance(hours: int = 3) -> None:
    """
    Проверять актуальность IP адресов всех записанных хостов через определенный промежуток
    Args:
        hours (int): Промежуток между проверками

    Returns:
        None:
    """
    while True:
        host_list = DATABASE.get_all_host_with_ip()
        for host in host_list.keys():
            lookup_ip = find_all_ip_hostname(hostname=host)
            db_host_ip = host_list[host]

            new_ip = set.difference(set(lookup_ip), set(db_host_ip))
            deleted_ip = set.difference(set(db_host_ip), set(lookup_ip))

            if new_ip:
                add_new_ip_all_service(hostname=host, ip_address_list=list(new_ip))

            if deleted_ip:
                for ip in deleted_ip:
                    try:
                        DATABASE.delete_ip_by_hostname(hostname=host, ip_address=ip)
                    except DoesNotExist:
                        continue

        await async_sleep(hours * 60 * 60)
