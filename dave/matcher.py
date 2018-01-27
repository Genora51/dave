from fuzzywuzzy import process, fuzz
import re
import spacy
from operator import itemgetter
from itertools import groupby


class Matcher(object):
    """Matches queries against a module."""

    def __init__(self, threshold=75):
        self.modules = [
            "hello", "joke", "about", "search"
        ]
        self.threshold = threshold

    def __call__(self, query):
        return self.match(query)

    def match(self, query):
        raise NotImplementedError


class NaiveMatcher(Matcher):
    """Naively matches modules."""
    def match(self, query):
        return process.extractOne(query, self.modules,
                                  score_cutoff=self.threshold)


class PartialMatcher(Matcher):
    """Matches partial words."""
    def match(self, query):
        return process.extractOne(query, self.modules,
                                  scorer=fuzz.partial_ratio,
                                  score_cutoff=self.threshold)


class TokensetMatcher(Matcher):
    """Places tokens into a set to match."""
    def match(self, query):
        return process.extractOne(query, self.modules,
                                  scorer=fuzz.token_set_ratio,
                                  score_cutoff=self.threshold)


class FirstMatcher(Matcher):
    """Matches against the first closely-matching module."""
    def regex_wordsplit(self, xs):
        return re.findall(r"[\w']+", xs)

    def match(self, query, string=True):
        if string:
            query = self.regex_wordsplit(query)
        for word in query:
            match = process.extractOne(
                word, self.modules,
                scorer=fuzz.ratio, score_cutoff=self.threshold
            )
            if match:
                return match


class SpacyMatcher(Matcher):
    """Uses an NLP tree to match modules."""
    def __init__(self, threshold=75):
        super().__init__(threshold)
        self.first_match = FirstMatcher(threshold=self.threshold)
        self.nlp = spacy.load('en')

    def nlp_tree(self, t, s=0):
        if t is not []:
            for word in t:
                if word.pos_ != 'PUNCT' and word.pos_ != 'SYM':
                    yield word.lemma_, s
                yield from self.nlp_tree(word.children, s + 1)

    def match(self, query):
        doc = self.nlp(query)
        tree = self.nlp_tree([next(doc.sents).root])
        for _, words in groupby(tree, itemgetter(1)):
            zp = list(zip(*words))
            fm = self.first_match(zp[0], string=False)
            if fm:
                return fm
