import socket
import re
from app.logger import get_logger


log = get_logger(__name__)


def find_all_ip_hostname(hostname: str, logging: bool = True) -> list:
    """
    Ищет все ip по заданному host
    Args:
        hostname (str): Название хоста, по которому необходимо найти ip
        logging (bool): Задействовать ли лог для найденных IP
    Returns:
        list: Список IP адресов
    """
    clear_hostname = re.sub(r'(\s+)', '', hostname)
    try:
        lookup_host = socket.gethostbyname_ex(clear_hostname)[-1]

        if logging:
            log.info(f"Для хоста {hostname} обнаружены ip: {', '.join(lookup_host)}")
        return lookup_host

    except socket.gaierror as err:
        log.error(f"Ошибка lookup хоста {hostname} - {err}")
        return []
