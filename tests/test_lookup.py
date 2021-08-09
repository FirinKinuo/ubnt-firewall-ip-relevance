from app.lookup import *


def test_find_id_by_hostname():
    assert find_all_ip_hostname("sberbank.ru") == ['194.54.14.168']
    assert find_all_ip_hostname('google.com') == ['142.251.1.139', '142.251.1.101', '142.251.1.113', '142.251.1.138',
                                                  '142.251.1.102', '142.251.1.100']
