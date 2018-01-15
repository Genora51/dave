from aiohttp import web
from daemons import Daemon
from os import path
import socketio

fdir = path.dirname(path.abspath(__file__))
uidir = path.join(fdir, 'ui')


def run_server(port):
    sio = socketio.AsyncServer()
    app = web.Application()
    sio.attach(app)

    async def index(request):
        """Serve the client-side application."""
        with open(path.join(uidir, 'index.html')) as f:
            return web.Response(text=f.read(), content_type='text/html')

    @sio.on('text request', namespace='/')
    async def text_request(sid, data):
        await sio.emit('plaintext reply', data, room=sid)

    @sio.on('speech request', namespace='/')
    async def speech_request(sid, data):
        await sio.emit('speech reply', "Hello, world!", room=sid)

    app.router.add_get('/', index)
    app.router.add_static('/', uidir)
    web.run_app(app, port=port)


class ServerDaemon(Daemon):
    """DAVE Server Daemon."""

    def __init__(self, port=5128):
        self.port = port
        self.pidpath = "/tmp/dave_server.pid"

    def run(self):
        run_server(self.port)


if __name__ == "__main__":
    server_daemon = ServerDaemon()
    server_daemon.run_daemon()
