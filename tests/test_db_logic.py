import pytest
import asyncio
import random
from app.database import Database
from app.database.models import *
from app.database.exceptions import *


def generate_random_host():
    return ''.join([random.choice('qwertyuiopasdfghl') for _ in range(5)]) + '.com'


@pytest.fixture(scope='session')
def loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope='session')
def init_db(loop):
    db = Database(database="test.sqlite")
    db.drop_all()
    loop.run_until_complete(db.init())
    yield db
    db.drop_all()


def test_add_hostname(init_db):
    hostname = 'add_host.test'

    added_host = init_db.add_new_host(hostname)

    assert isinstance(added_host, Host)
    with pytest.raises(IntegrityError):
        init_db.add_new_host(hostname)


def test_add_new_ip(init_db):
    hostname_payload = init_db.get_or_create_host_by_name(generate_random_host())
    ip_payload = '192.168.12.12'

    added_ip = init_db.add_host_ip(hostname=hostname_payload, ip_address=ip_payload)

    assert isinstance(added_ip, IpAddress)


def test_add_new_ip_list(init_db):
    hostname_payload = init_db.get_or_create_host_by_name(generate_random_host())
    ip_payload = [
        '192.168.12.12',
        '192.168.12.13',
        '192.168.12.14'
    ]

    added_ip_list = init_db.add_host_ip_list(hostname=hostname_payload, ip_list=ip_payload)

    assert isinstance(added_ip_list, list)


def test_ip_unique(init_db):
    hostname_payload = init_db.get_or_create_host_by_name(generate_random_host() + '.test')
    ip_payload = [
        '192.168.13.12',
        '192.168.13.13',
        '192.168.13.14'
    ]
    init_db.add_host_ip_list(hostname=hostname_payload, ip_list=ip_payload)

    repeat_added_ip_list = init_db.add_host_ip_list(hostname=hostname_payload, ip_list=ip_payload)

    if repeat_added_ip_list:
        raise AssertionError("IP адрес не должен быть добавлен")


def test_get_hostname_list(init_db):
    hostname_payload = init_db.get_or_create_host_by_name('get_host_list.test')
    init_db.add_new_host(hostname=hostname_payload)

    host_list = init_db.get_host_list()

    assert isinstance(host_list, list)


def test_get_ip_address_list(init_db):
    host_payload = init_db.get_or_create_host_by_name('get_ip.test.com')
    init_db.add_host_ip_list(host_payload, ['192.168.222.23', '192.168.142.24'])

    ip_added_list = init_db.get_host_ip_list(hostname=host_payload)

    assert ip_added_list == ['192.168.222.23', '192.168.142.24']


def test_delete_ip_by_hostname(init_db):
    host_payload = init_db.get_or_create_host_by_name('delete_ip.test.com')
    ip_payload = ['192.168.122.23', '192.168.122.24']
    init_db.add_host_ip_list(hostname=host_payload, ip_list=ip_payload)

    init_db.delete_ip_by_hostname(hostname=host_payload, ip_address='192.168.122.23')

    assert '192.168.122.23' not in init_db.get_host_ip_list(hostname=host_payload)
    with pytest.raises(DoesNotExist):
        init_db.delete_ip_by_hostname(hostname=host_payload, ip_address='192.168.122.25')


def test_delete_hostname(init_db):
    host_payload = init_db.get_or_create_host_by_name('delete_host.test.com')
    ip_payload = ['192.168.123.23', '192.168.123.24']
    init_db.add_host_ip_list(hostname=host_payload, ip_list=ip_payload)

    init_db.delete_hostname(hostname=host_payload)

    assert host_payload not in init_db.get_host_list()
    assert ip_payload != init_db.get_host_ip_list(hostname=host_payload)


def test_get_hostname_with_ip(init_db):
    hostname_payload = init_db.get_or_create_host_by_name('get_host_with_ip.test')
    init_db.add_new_host(hostname=hostname_payload)

    host_list = init_db.get_all_host_with_ip()
    assert isinstance(host_list, dict)
