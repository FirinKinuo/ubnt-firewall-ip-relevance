from app.lookup import *


def test_find_id_by_hostname():
    host_payload = "localhost"

    ip_host = find_all_ip_hostname(hostname=host_payload)

    assert ip_host == ['127.0.0.1']
