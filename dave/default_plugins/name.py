import random


class DaveName:
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        responses = [
            "I am",
            "My name is",
            "I am called"
        ]
        response = "{} Dave.".format(random.choice(responses))
        yield "msg; say", response


def setup(app):
    app.register_aliases(["name", "called"], DaveName)