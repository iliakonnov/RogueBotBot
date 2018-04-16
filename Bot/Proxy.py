"""
Based on https://stackoverflow.com/a/39233701
Перенаправляет всё через прокси, указанный в конфиге и заставляет использовать только ipv4 (PySocks не поддерживает ipv6)
"""

import ssl
from http.client import HTTPConnection
import urllib3
import socks
import socket
from urllib3.connection import VerifiedHTTPSConnection

from Bot import Config


host, port = Config.proxy.rsplit(':', 1)
proxy_type, host = host.split('://', 1)
socks.set_default_proxy({
    'http': socks.HTTP,
    'socks4': socks.SOCKS4,
    'socks5': socks.SOCKS5
}[proxy_type.lower()], host, int(port))
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
