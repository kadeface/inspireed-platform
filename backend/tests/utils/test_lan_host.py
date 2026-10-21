from app.utils.lan_host import choose_lan_ipv4, is_lan_ipv4


def test_private_lan_addresses_are_accepted():
    assert is_lan_ipv4("192.168.1.20")
    assert is_lan_ipv4("10.0.0.8")
    assert is_lan_ipv4("172.16.0.4")


def test_loopback_public_and_virtual_addresses_are_rejected():
    assert not is_lan_ipv4("127.0.0.1")
    assert not is_lan_ipv4("localhost")
    assert not is_lan_ipv4("8.8.8.8")
    assert not is_lan_ipv4("198.18.0.1")
    assert not is_lan_ipv4("")


def test_choose_lan_ipv4_prefers_a_wifi_address():
    assert choose_lan_ipv4(["198.18.0.1", "192.168.1.101"]) == "192.168.1.101"
    assert choose_lan_ipv4(["10.0.0.8", "192.168.1.101"]) == "192.168.1.101"
    assert choose_lan_ipv4(["", "127.0.0.1", "192.168.2.35"]) == "192.168.2.35"
    assert choose_lan_ipv4(["127.0.0.1"]) is None
