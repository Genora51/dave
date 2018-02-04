import random


class HelloSayer:
    aliases = ["hi", "hello", "hey"]

    def __init__(self, data):
        self.data = data

    def __iter__(self):
        greeting = random.choice(self.aliases).capitalize()
        if random.getrandbits(1):
            if random.getrandbits(1):
                greeting += ','
            greeting += ' there'
        if random.getrandbits(1):
            greeting += '.'
        else:
            greeting += '!'
        yield "msg; say", greeting


def setup(app):
    app.register_aliases(HelloSayer.aliases, HelloSayer)
