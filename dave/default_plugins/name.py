import random


class DaveName:
    def __init__(self, data):
        self.data = data

    async def __aiter__(self):
        # Pick from a list of responses
        responses = [
            "I am",
            "My name is",
            "I am called"
        ]
        response = "{} Dave.".format(random.choice(responses))
        yield "msg; say", response


def setup(app):
    app.register_aliases(["name", "called"], DaveName)
