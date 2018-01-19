from fuzzywuzzy import process


class Matcher(object):
    """Matches queries against a module."""

    def __init__(self):
        self.modules = [
            "hello", "joke", "about", "search"
        ]

    def __call__(self, query):
        raise NotImplementedError


class NaiveMatcher(Matcher):
    """Naively matches modules."""
    def __call__(self, query):
        return process.extractOne(query, self.modules)
