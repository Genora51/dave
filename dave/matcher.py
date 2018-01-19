from fuzzywuzzy import process, fuzz


class Matcher(object):
    """Matches queries against a module."""

    def __init__(self, threshold=75):
        self.modules = [
            "hello", "joke", "about", "search"
        ]
        self.threshold = threshold

    def __call__(self, query):
        raise NotImplementedError


class NaiveMatcher(Matcher):
    """Naively matches modules."""
    def __call__(self, query):
        return process.extractOne(query, self.modules,
                                  score_cutoff=self.threshold)


class PartialMatcher(Matcher):
    """Matches partial words."""
    def __call__(self, query):
        return process.extractOne(query, self.modules,
                                  scorer=fuzz.partial_ratio,
                                  score_cutoff=self.threshold)


class TokensetMatcher(Matcher):
    """Places tokens into a set to match."""
    def __call__(self, query):
        return process.extractOne(query, self.modules,
                                  scorer=fuzz.token_set_ratio,
                                  score_cutoff=self.threshold)
