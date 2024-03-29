import aiohttp
import json
import random
import time


class JokeTeller:
    def __init__(self, data):
        self.data = data
        self.rand = random.Random(time.time())

    async def __aiter__(self):
        if len(self.data["keywords"]) > 0:
            joke = self.find_joke()
        else:
            joke = self.rand_joke()
        async for cmd in joke:
            yield cmd

    async def find_joke(self):
        """Search r/jokes (reddit) for a joke."""
        # Try for each keyword
        kw = " ".join(w.orth_ for w in self.data["keywords"])
        # Create url from search term
        opts = {
            'q': 'nsfw:no "{}" NOT flair:Long'.format(kw),
            'sort': 'top',
            'syntax': 'plain',
            'restrict_sr': 'on',
            'limit': '10'
        }
        url = "https://reddit.com/r/jokes/search.json"
        # Read json from request
        async with aiohttp.ClientSession() as client:
            async with client.get(url, params=opts) as resp:
                jstring = await resp.read()
                res = json.loads(jstring)['data']['children']
        # If jokes found, pick one
        if len(res) > 0:
            joke_j = self.rand.choice(res)["data"]
            # Create list of lines from joke
            joke = [joke_j["title"]]
            txt = list(filter(
                lambda x: x != '',
                joke_j["selftext"].splitlines()
            ))
            joke += txt
            # Read each line, then break loop
            for line in joke:
                yield "msg; say", line
        else:  # If no joke found, get random joke
            async for cmd in self.rand_joke():
                yield cmd

    async def rand_joke(self):
        """Get a random joke from reddit's r/jokes."""
        # URL to get a random joke in json form
        url = "https://reddit.com/r/jokes/random.json"
        # Read json from url
        async with aiohttp.ClientSession() as client:
            async with client.get(url) as resp:
                jstring = await resp.read()
                res = json.loads(jstring)[0]['data']['children']
        if len(res) > 0:
            # Get each line of joke and read it
            joke_j = res[0]["data"]
            joke = [joke_j["title"]]
            txt = list(filter(
                lambda x: x != '',
                joke_j["selftext"].splitlines()
            ))
            joke += txt
            for line in joke:
                yield "msg; say", line


def setup(app):
    app.register_aliases(["joke"], JokeTeller)
