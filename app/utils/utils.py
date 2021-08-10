from dotenv import load_dotenv
from asyncio import sleep as async_sleep
from app.setting import DOT_ENV_PATH
from app.lookup import find_all_ip_hostname
from app.database.exceptions import DoesNotExist


def load_env_file() -> None:
    """
    Загружает данные из файла с виртуальным окружением, если данный файл невозможно прочитать, то скрипт завершается
    Returns:
        None:
    """
    load_dotenv(DOT_ENV_PATH)


async def background_checking_relevance(db, hours: int = 3) -> None:
    """
    Проверять актуальность IP адресов всех записанных хостов через определенный промежуток
    Args:
        db (Database): Используемый экземпляр базы данных
        hours (int): Промежуток между проверками

    Returns:
        None:
    """
    while True:
        host_list = db.get_all_host_with_ip()
        for host in host_list.keys():
            lookup_ip = find_all_ip_hostname(hostname=host)
            db_host_ip = host_list[host]

            new_ip = set.difference(set(lookup_ip), set(db_host_ip))
            deleted_ip = set.difference(set(db_host_ip), set(lookup_ip))

            if new_ip:
                db.add_host_ip_list(hostname=host, ip_list=new_ip)

            if deleted_ip:
                host_id = db.get_host_id(hostname=host)
                for ip in deleted_ip:
                    try:
                        db.delete_ip_by_hostname(hostname_id=host_id, ip_address=ip)
                    except DoesNotExist:
                        continue

        await async_sleep(hours * 60 * 60)
