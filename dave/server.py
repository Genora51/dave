from aiohttp import web
from daemons import Daemon
from os import path
import socketio
import os
import speech_recognition as sr
import matcher
import runner
import spacy

fdir = path.dirname(path.abspath(__file__))
uidir = path.join(fdir, 'ui')


def run_server(port):
    sio = socketio.AsyncServer()
    app = web.Application()
    sio.attach(app)
    module_match = matcher.SpacyMatcher()
    nlp = spacy.load('en')
    module_match.nlp = nlp

    async def index(request):
        """Serve the client-side application."""
        with open(path.join(uidir, 'index.html')) as f:
            return web.Response(text=f.read(), content_type='text/html')

    @sio.on('text request', namespace='/')
    async def text_request(sid, data):
        module_name, module = module_match(data)
        print(module_name, module)
        if module_name is not None:
            m_data = runner.extract_data(
                data, module_name,
                module_match, nlp
            )
            for response in runner.run_module(module, m_data):
                await sio.emit('plaintext reply', response, room=sid)        

    @sio.on('speech request', namespace='/')
    async def speech_request(sid, data):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            message = [r.recognize_google(audio, language="en-GB"), False]
        except (sr.UnknownValueError, sr.RequestError):
            message = ["Sorry, I didn't understand that.", True]
        await sio.emit('speech reply', message, room=sid)

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
        os.kill(pid, 15)

if __name__ == "__main__":
    server_daemon = ServerDaemon()
    server_daemon.run_daemon()
