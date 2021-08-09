import socket


def find_all_ip_hostname(hostname: str) -> list:
    """
    Ищет все ip по заданному host
    Args:
        hostname (str): Название хоста, по которому необходимо найти ip

    Returns:
        list: Список IP адресов
    """
    return socket.gethostbyname_ex(hostname)[-1]

