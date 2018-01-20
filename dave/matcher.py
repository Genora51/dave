from fuzzywuzzy import process, fuzz
import re


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


class FirstMatcher(Matcher):
    """Matches against the first closely-matching module."""
    def regex_wordsplit(self, xs):
        return re.findall(r"[\w']+", xs)

    def __call__(self, query, string=True):
        if string:
            query = self.regex_wordsplit(query)
        for word in query:
            match = process.extractOne(
                word, self.modules,
                scorer=fuzz.ratio, score_cutoff=self.threshold
            )
            if match:
                return match
