from aiohttp import web
from daemons import Daemon
from os import path


class ServerDaemon(Daemon):
    """DAVE Server Daemon."""

    def __init__(self, port=5128):
        fdir = path.dirname(path.abspath(__file__))
        uidir = path.join(fdir, 'ui')
        self.port = port
        self.pidpath = "/tmp/dave_server.pid"
        self.app = web.Application()
        self.app.router.add_static('/', uidir)

    def run(self):
        web.run_app(self.app, port=self.port)

if __name__ == "__main__":
    server_daemon = ServerDaemon()
    server_daemon.run_daemon()
