"""
Based on https://stackoverflow.com/a/39233701
Перенаправляет всё через прокси, указанный в конфиге и заставляет использовать только ipv4 (PySocks не поддерживает ipv6)
"""

import ssl
from urllib import parse
from http.client import HTTPConnection
import urllib3
import socks
import socket
from urllib3.connection import VerifiedHTTPSConnection

from Bot import Config


parsed: parse.ParseResult = parse.urlparse(Config.proxy)
proxy_types = proxy_type = {
    'http': socks.HTTP,
    'socks4': socks.SOCKS4,
    'socks5': socks.SOCKS5,
    'socks': socks.SOCKS5
}

if parsed.scheme == 'tg' or parsed.hostname == 't.me':
    if parsed.scheme == 'tg':
        proxy_type = proxy_type[parsed.hostname]
    elif parsed.hostname == 't.me':
        proxy_type = proxy_type[parsed.path.strip('/')]
    parsed_query = parse.parse_qs(parsed.query)
    host = parsed_query['server'][0]
    port = parsed_query['port'][0]
    if 'user' in parsed_query and 'pass' in parsed_query:
        username = parsed_query['user'][0]
        password = parsed_query['pass'][0]
    else:
        username, password = None, None
else:
    proxy_type = proxy_types[parsed.scheme]
    host = parsed.hostname
    port = parsed.port
    username = parsed.username
    password = parsed.password

socks.set_default_proxy(proxy_type, host, int(port), username=username, password=password)
socket.socket = socks.socksocket


# HTTP
class MyHTTPConnection(HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_INET)
        self.sock.connect((self.host, self.port))
        if self._tunnel_host:
            self._tunnel()


urllib3.connectionpool.HTTPConnection = MyHTTPConnection
urllib3.connectionpool.HTTPConnectionPool.ConnectionCls = MyHTTPConnection


# HTTPS
class MyHTTPSConnection(VerifiedHTTPSConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_INET)
        self.sock.connect((self.host, self.port))
        if self._tunnel_host:
            self._tunnel()
        self.sock = ssl.wrap_socket(self.sock, self.key_file, self.cert_file)


urllib3.connectionpool.HTTPSConnection = MyHTTPSConnection
urllib3.connectionpool.VerifiedHTTPSConnection = MyHTTPSConnection
urllib3.connectionpool.HTTPSConnectionPool.ConnectionCls = MyHTTPSConnection

try:
    import telepot
except ImportError:
    pass
else:
    telepot.api.urllib3 = urllib3
