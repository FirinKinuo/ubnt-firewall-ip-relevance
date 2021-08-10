import pytest
import os
from pathlib import Path
from app.file import *


@pytest.fixture(scope='session', name="host_file")
def create_test_file():
    test_file = Path("temp_test.txt")
    with open(test_file, 'w') as host_file:
        host_file.write("sberbank.ru\nvk.com")

    yield test_file

    os.remove(test_file)


def test_search_new_host_from_file(host_file):
    host_file = HostFile(host_file_path=host_file)

    new_hosts = host_file.find_new_host()

    assert new_hosts == ['sberbank.ru', 'vk.com']
