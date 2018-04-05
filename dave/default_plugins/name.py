import random


def say_name(data):
    # Pick from a list of responses
    responses = [
        "I am",
        "My name is",
        "I am called"
    ]
    response = "{} Dave.".format(random.choice(responses))
    yield "msg; say", response


def setup(app):
    app.register_aliases(["name", "called"], say_name)
