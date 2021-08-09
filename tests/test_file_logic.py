import pytest
from pathlib import Path
from app.file import *


@pytest.fixture(scope='session', name="host_file")
def create_test_file():
    test_file = Path("temp_test.txt")
    with open(test_file, 'w') as host_file:
        host_file.write("google.com\nsberbank.ru\nvk.com")

    return test_file


def test_search_new_host_from_file(host_file):
    host_file = HostFile(host_file_path=host_file)
    assert host_file.find_new_host() == ['sberbank.ru', 'vk.com']
