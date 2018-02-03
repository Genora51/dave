import urllib
import json
import random
import time


class JokeTeller:
    def __init__(self, data):
        self.data = data
        self.rand = random.Random(time.time())

    def __iter__(self):
        for kw in self.data["keywords"]:
            opts = urllib.parse.urlencode({
                'q': 'nsfw:no "{}" NOT flair:Long'.format(kw),
                'sort': 'top',
                'syntax': 'plain',
                'restrict_sr': 'on',
                'limit': '10'
            })
            url = "https://reddit.com/r/jokes/search.json?{}".format(opts)
            request = urllib.request.Request(url)
            with urllib.request.urlopen(request) as response:
                res = json.load(response)['data']['children']
            if len(res) > 0:
                joke_j = self.rand.choice(res)["data"]
                joke = [joke_j["title"]]
                txt = list(filter(
                    lambda x: x != '',
                    joke_j["selftext"].splitlines()
                ))
                joke += txt
                for line in joke:
                    yield "msg; say", line
                break


def setup(app):
    app.register_aliases(["joke"], JokeTeller)
