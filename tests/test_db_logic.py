from dotenv import get_key as env_get_key
import pytest
import asyncio
import random
from app.database import Database
from app.setting import DOT_ENV_PATH
from app.database.models import *
from app.database.exceptions import *

HOST_NAME_TEST = 'google.com'


def generate_random_host():
    return ''.join([random.choice('qwertyuiopasdfghl') if i != 5 else random.choice('ABC') for i in range(5)]) + '.com'


@pytest.fixture(scope='session')
def loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope='session')
def init_db(loop):
    db = Database(database=env_get_key(DOT_ENV_PATH, 'SQLITE_PATH'))
    db.drop_all()
    loop.run_until_complete(db.init())
    return db


def test_add_hostname(init_db):
    assert isinstance(init_db.add_new_host(HOST_NAME_TEST), Host)


def test_add_repeat_hostname(init_db):
    with pytest.raises(IntegrityError):
        init_db.add_new_host(HOST_NAME_TEST)


def test_add_new_ip(init_db):
    assert isinstance(init_db.add_host_ip(hostname=generate_random_host(), ip_address='192.168.12.12'), IpAddress)


def test_add_new_ip_list(init_db):
    assert isinstance(init_db.add_host_ip_list(hostname=generate_random_host(), ip_list=[
        '192.168.12.12',
        '192.168.12.13',
        '192.168.12.14'
    ]), list)


def test_ip_unique(init_db):
    test_host = generate_random_host() + '.test'
    ip_address_list = [
        '192.168.13.12',
        '192.168.13.13',
        '192.168.13.14'
    ]

    init_db.add_host_ip_list(hostname=test_host, ip_list=ip_address_list)

    repeat_added_ip_list = init_db.add_host_ip_list(hostname=test_host, ip_list=ip_address_list)

    if repeat_added_ip_list:
        raise AssertionError("IP адрес не должен быть добавлен")

