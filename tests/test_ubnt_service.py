import pytest
from app.ubnt import UbntService

# Так как для тестов необходимо использовать настоящее оборудование, то у некоторых может возникнуть проблема
# С тестированием, тогда стоит отключить данный тест
SKIP_THIS_TEST_MODULE = True

# Параметры для входа по SSH
SSH_UBNT_TEST_HOST = '192.168.1.1'
SSH_UBNT_TEST_LOGIN = 'ubnt'
SSH_UBNT_TEST_PASSWORD = 'ubnt'
SSH_UBNT_TEST_KEY_PATH = None


@pytest.fixture(scope='session', name='ubnt')
def connect_to_ubnt_ssh():
    ubnt = UbntService(
        host=SSH_UBNT_TEST_HOST,
        login=SSH_UBNT_TEST_LOGIN,
        password=SSH_UBNT_TEST_PASSWORD,
        key=SSH_UBNT_TEST_KEY_PATH,
        firewall_group='test-v4'
    )

    return ubnt


@pytest.mark.skipif(SKIP_THIS_TEST_MODULE, reason="Невозможно подключиться к тестовой платформе")
def test_add_ip_firewall(ubnt):
    ip_payload = ['192.168.10.1', '192.168.11.3']

    ubnt.add_new_ip(ip_address_list=ip_payload)


@pytest.mark.skipif(SKIP_THIS_TEST_MODULE, reason="Невозможно подключиться к тестовой платформе")
def test_delete_ip_firewall(ubnt):
    ip_payload = ['192.168.10.1', '192.168.11.3']

    ubnt.add_new_ip(ip_address_list=ip_payload)
    ubnt.delete_ip(ip_address_list=ip_payload)
