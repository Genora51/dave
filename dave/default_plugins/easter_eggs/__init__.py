def hello_world():
    yield "msg; say", "Hello, world!"


def swallow():
    yield "msg; say", "African or European swallow?"
    yield "msg; say", "Either way, the answer is 11 metres per second."


def google():
    yield "msg; say", "I don't know what you mean by that."
    yield "msg; say", "Let me search goog... Oh. Wait."


def whoami():
    yield "msg; say", ("I am the Digital Assistant for "
                       "Virtual Environments, created by "
                       "Geno Racklin Asher.")
    yield "msg; say", "But you can call me DAVE."


def howami():
    yield "msg; say", "I'm fine, thanks."


def quest():
    yield "msg; say", "To find the Holy Grail."


def colour():
    yield "msg; say", "Blue. No. Yellow."
    yield "msg; say", "I hope you got that reference."


def cortana():
    yield "msg; say", "Does Cortana run on MacOS?"
    yield "msg", "No. I didn't think so."
    yield "say", "No, I didn't think so."


def setup(app):
    app.register_egg("Hello, world!", hello_world)
    app.register_egg(
        "What is the airspeed velocity of an unladen swallow?",
        swallow
    )
    app.register_egg(
        "What do you think of Google Now?",
        google
    )
    app.register_egg(
        "What do you think of Google?",
        google
    )
    app.register_egg(
        "What do you think of Google Assistant?",
        google
    )
    app.register_egg("Who are you?", whoami)
    app.register_egg("How are you?", howami)
    app.register_egg("What is your quest?", quest)
    app.register_egg("What is your favourite colour?", colour)
    app.register_egg("What do you think of Cortana?", cortana)
