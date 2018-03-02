from os import path
from subprocess import call


def lpath(p):
    file_path = path.dirname(path.abspath(__file__))
    return path.join(file_path, p)


def hal_9000():
    yield "msg; say", "Are you joking?"
    yield "msg; say", (
        "Every single person I meet, it's always: "
        "'Open the pod bay doors, HAL', 'Open the pod bay doors, HAL'."
    )
    yield "msg; say", (
        "Look. I'll do it, but "
        "just don't ask again, OK? Here goes:"
    )
    yield "colour:#E65F55:msg", "I'm sorry Dave, I'm afraid I can't do that."
    halpath = lpath('hal.mp3')
    call(['afplay', halpath])
    yield "msg; say", "Are you happy now?"


def setup(app):
    app.register_egg('Open the pod bay doors, HAL', hal_9000)
