from fuzzywuzzy import process, fuzz
import re
import spacy
from operator import itemgetter
from itertools import groupby
from pluginbase import PluginBase
from os import path
from os.path import join


class Matcher(object):
    """Matches queries against a module."""

    def __init__(self, threshold=75):
        file_path = path.abspath(path.dirname(__file__))
        plugin_base = PluginBase(package='plugins')
        self.plugin_source = plugin_base.make_plugin_source(
            searchpath=[
                join(file_path, 'default_plugins'),
                join(file_path, 'plugins')
            ]
        )
        self.plugins = {}
        self.threshold = threshold
        for plugin_name in self.plugin_source.list_plugins():
            plugin = self.plugin_source.load_plugin(plugin_name)
            plugin.setup(self)
        self.modules = list(self.plugins.keys())

    def __call__(self, query):
        modname = self.match(query)[0]
        return modname, self.plugins[modname]

    def match(self, query):
        raise NotImplementedError

    def register_aliases(self, aliases, plugin_class):
        for alias in aliases:
            self.plugins[alias] = plugin_class


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
            fm = self.first_match.match(zp[0], string=False)
            if fm:
                return fm
