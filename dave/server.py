from aiohttp import web
from .daemons import Daemon
from os import path
import socketio
import os
import speech_recognition as sr
from . import matcher, runner
import spacy

# Get file directory
fdir = path.dirname(path.abspath(__file__))
uidir = path.join(fdir, 'ui')


def run_server(port):
    """Run the aiohttp DAVE server."""
    sio = socketio.AsyncServer()  # Initialise socketio
    app = web.Application()
    sio.attach(app)  # Link socketio to aiohttp server app
    module_match = matcher.SpacyMatcher()
    nlp = spacy.load('en')
    module_match.nlp = nlp
    loop_runner = runner.InputRunner(module_match)

    async def index(request):
        """Serve the client-side application."""
        with open(path.join(uidir, 'index.html')) as f:
            return web.Response(text=f.read(), content_type='text/html')

    @sio.on('text request', namespace='/')
    async def text_request(sid, data):
        """Handle text-based DAVE request."""
        # Attempt to get best-match module
        async for form, response in loop_runner(data):
            await sio.emit(form, response, room=sid)

    @sio.on('speech request', namespace='/')
    async def speech_request(sid, data):
        """Handle speech recognition."""
        r = sr.Recognizer()
        # Attempt to recognise audio
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            message = [r.recognize_google(audio, language="en-GB"), False]
        except (sr.UnknownValueError, sr.RequestError):
            message = ["Sorry, I didn't understand that.", True]
        # Emit [message, isDave] with socketio
        await sio.emit('speech reply', message, room=sid)

    # Initialise routes and start server.
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

    def shutdown(self, pid):
        """Shuts down socketio connections."""
        # TODO: Replace this hack with a more elegant shutdown.
        os.kill(pid, 15)


def main():
    server_daemon = ServerDaemon()
    server_daemon.run_daemon()


if __name__ == "__main__":
    main()
