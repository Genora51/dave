class AppOpener:
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        yield "msg; say", "Hello, World!"


def setup(app):
    ao_aliases = ["open", "run", "start", "launch"]
    app.register_aliases(ao_aliases, AppOpener)
