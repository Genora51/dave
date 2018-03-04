import aiohttp
import json
from string import Template
from bs4 import BeautifulSoup


class WebFallback:
    def __init__(self, data):
        self.data = data

    async def __aiter__(self):
        # Create DuckDuckGo instant answer query
        url = "https://api.duckduckgo.com"
        opts = {
            "q": " ".join(x.orth_.lower() for x in self.data["keywords"]),
            "format": "json"
        }
        # Execute query to get JSON response
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=opts) as resp:
                jstring = await resp.read()
                res = json.loads(jstring)
        # Build HTML reply template
        template = [
            '<h3>$Heading</h3>',
            '$Abstract',
            '<a href="$AbstractURL">',
            '<br/> $Heading - $AbstractSource'
            '</a>'
        ]
        if res["Image"]:
            template.insert(-2, '<img src="$Image">')
        if not res["Abstract"]:
            abstract = BeautifulSoup(
                res["RelatedTopics"][0]["Result"], "html5lib"
            )
            sections = " ".join(
                x for x in abstract.find('body').children if isinstance(x, str)
            )
            res["Abstract"] = sections
            if not res["Image"]:
                res["RelatedTopics"][0]["Icon"]["URL"]
        # Only first sentence
        res["Abstract"] = next(self.data["nlp"](res["Abstract"]).sents).string
        # Convert template to string
        s = Template(" ".join(template))
        html = s.safe_substitute(res)
        # Yield response
        yield "html", html
        yield "say", res["Abstract"]


def setup(app):
    app.register_aliases(["about"], WebFallback)
    app.register_fallback(WebFallback)
