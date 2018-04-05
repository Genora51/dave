import random

aliases = ["hi", "hello", "hey"]


def say_hello(data):
    greeting = random.choice(aliases).capitalize()
    # Sometimes add ',' and/or 'there'
    if random.getrandbits(1):
        if random.getrandbits(1):
            greeting += ','
        greeting += ' there'
    # Choose between full stop and exclamation mark
    if random.getrandbits(1):
        greeting += '.'
    else:
        greeting += '!'
    yield "msg; say", greeting


def setup(app):
    app.register_aliases(aliases, say_hello)
