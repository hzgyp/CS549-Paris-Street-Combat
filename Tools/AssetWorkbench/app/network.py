"""Discover local IPv4 authorities for the shared workbench; never allow arbitrary Host values."""
import ipaddress
import socket
import re
from urllib.parse import urlsplit


def external_origin(value=None, shared=False):
    """Only the explicitly configured HTTP authority may cross a port forward."""
    if not shared or value in (None, ''):
        return None
    if not isinstance(value, str) or any(ord(c) <= 32 for c in value):
        raise ValueError('external_url must be an HTTP URL without whitespace')
    try:
        parsed=urlsplit(value)
        host=parsed.hostname
        port=parsed.port or 80
    except ValueError as e:
        raise ValueError('Invalid external_url host or port') from e
    if (parsed.scheme!='http' or not host or parsed.username is not None or parsed.password is not None
            or parsed.path not in ('','/') or parsed.query or parsed.fragment or ':' in host
            or parsed.port==0):
        raise ValueError('external_url must contain only an HTTP IPv4/DNS host and port')
    if len(host)>253 or not all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',label) for label in host.split('.')):
        raise ValueError('Invalid external_url hostname')
    authority=host if port==80 else f'{host}:{port}'
    return f'http://{authority}'


def addresses(shared=False):
    if not shared:
        return ['127.0.0.1'], ['127.0.0.1','localhost']
    discovered=set()
    try:
        discovered.update(row[4][0] for row in socket.getaddrinfo(socket.gethostname(),None,socket.AF_INET))
    except OSError:
        pass
    primary=None
    try:
        # UDP connect only selects the local routing interface; no datagram is sent.
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as route:
            route.connect(('192.0.2.1',9))
            primary=route.getsockname()[0]
            discovered.add(primary)
    except OSError:
        pass
    ips=sorted(ip for ip in discovered if not ipaddress.ip_address(ip).is_loopback and not ipaddress.ip_address(ip).is_link_local)
    if primary in ips:
        ips.remove(primary);ips.insert(0,primary)
    hosts=['127.0.0.1','localhost',socket.gethostname().lower(),*ips]
    return ips,list(dict.fromkeys(hosts))
