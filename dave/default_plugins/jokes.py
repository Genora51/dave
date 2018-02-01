import urllib


class JokeTeller:
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        for kw in self.data["keywords"]:
            opts = urllib.parse.urlencode({
                'term': kw.lemma_,
                'limit': 1
            })
            url = "https://icanhazdadjoke.com/search?{}".format(opts)
            headers = {"Accept": "text/plain", 'User-Agent': 'Mozilla/5.0'}
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request) as response:
                res = response.read().decode("utf-8")
            if len(res) > 0:
                yield "msg; say", res
                break


def setup(app):
    app.register_aliases(["joke"], JokeTeller)
