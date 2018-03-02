from . import basic_eggs, sound_eggs


def setup(app):
    basic_eggs.setup(app)
    sound_eggs.setup(app)
