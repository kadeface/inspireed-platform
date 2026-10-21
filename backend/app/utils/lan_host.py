"""本机局域网 IPv4，供教师在 127.0.0.1 打开页面时生成手机可访问的地址。"""

import ipaddress
import socket
import subprocess
from typing import Optional


def is_lan_ipv4(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value.strip())
    except ValueError:
        return False
    if not isinstance(ip, ipaddress.IPv4Address) or ip.is_loopback:
        return False
    networks = (
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.168.0.0/16"),
    )
    return any(ip in network for network in networks)


def _rank(ip: str) -> int:
    if ip.startswith("192.168."):
        return 0
    if ip.startswith("10."):
        return 1
    return 2


def choose_lan_ipv4(candidates: list[str]) -> Optional[str]:
    accepted: list[str] = []
    for candidate in candidates:
        text = candidate.strip()
        if is_lan_ipv4(text) and text not in accepted:
            accepted.append(text)
    if not accepted:
        return None
    accepted.sort(key=_rank)
    return accepted[0]


def _interface_ipv4s() -> list[str]:
    commands = (["ifconfig"], ["ip", "-4", "-o", "addr"])
    for command in commands:
        try:
            out = subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL, timeout=2)
        except (OSError, subprocess.SubprocessError):
            continue
        found = []
        for line in out.splitlines():
            parts = line.split()
            if "inet" not in parts:
                continue
            addr = parts[parts.index("inet") + 1].split("/")[0]
            found.append(addr)
        if found:
            return found
    return []


def detect_lan_ipv4() -> Optional[str]:
    """选出手机能访问的私网 IPv4。优先 192.168，避开代理虚拟网卡。"""
    candidates = _interface_ipv4s()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            candidates.append(sock.getsockname()[0])
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            candidates.append(info[4][0])
    except OSError:
        pass
    return choose_lan_ipv4(candidates)
