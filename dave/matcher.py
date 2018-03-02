from fuzzywuzzy import process, fuzz
import re
from operator import itemgetter
from itertools import groupby
from pluginbase import PluginBase
from os import path
from os.path import join


class Matcher(object):
    """Matches queries against a module."""

    def __init__(self, threshold=75, egg_threshold=85):
        self.threshold = threshold
        self.egg_threshold = egg_threshold
        # Location of this script
        file_path = path.abspath(path.dirname(__file__))
        # Create pluginbase
        plugin_base = PluginBase(package='plugins')
        self.plugin_source = plugin_base.make_plugin_source(
            searchpath=[
                join(file_path, 'default_plugins'),
                join(file_path, 'plugins')
            ]
        )
        # Load all plugins
        self.plugins = {}
        self.eggs = {}
        for plugin_name in self.plugin_source.list_plugins():
            plugin = self.plugin_source.load_plugin(plugin_name)
            plugin.setup(self)
        self.modules = list(self.plugins.keys())
        self.egg_names = list(self.eggs.keys())

    def __call__(self, query):
        """Get closest matching module."""
        modname = self.match(query)  # Returns (str, int) or None
        if modname:
            return modname[0], self.plugins[modname[0]]
        else:
            return None, None

    def match(self, query):
        raise NotImplementedError

    def register_aliases(self, aliases, plugin_class):
        """Add aliases for a plugin."""
        for alias in aliases:
            self.plugins[alias] = plugin_class

    def register_egg(self, easter_egg, egg_func):
        """Add an easter egg."""
        self.eggs[easter_egg] = egg_func

    def egg_match(self, query):
        """Get an easter egg."""
        eggname = self._egg_module(query)
        if eggname:
            return eggname[0], self.eggs[eggname[0]]
        else:
            return None, None

    def _egg_module(self, query):
        """Match against an easter egg."""
        return process.extractOne(query, self.egg_names,
                                  scorer=fuzz.ratio,
                                  score_cutoff=self.egg_threshold)


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
        if string:  # Is the query a string or a list?
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
    def __init__(self, threshold=75, egg_threshold=85):
        super().__init__(threshold, egg_threshold)
        self.first_match = FirstMatcher(threshold=self.threshold)
        # The NLP processor is assigned outside the class, after init
        self.nlp = None

    def nlp_tree(self, t, s=0):
        """Iterate through a SpaCy tree."""
        if t is not []:
            for word in t:
                # Ignore symbols & punctuation
                if word.pos_ != 'PUNCT' and word.pos_ != 'SYM':
                    yield word.lemma_, s
                yield from self.nlp_tree(word.children, s + 1)

    def match(self, query):
        doc = self.nlp(query)
        tree = self.nlp_tree([next(doc.sents).root])
        # Iterate through each "branch level" of the tree
        for _, words in groupby(tree, itemgetter(1)):
            # list of (str, token) -> (list of str, list of tokens)
            zp = list(zip(*words))
            # Attempt to get first matching module
            fm = self.first_match.match(zp[0], string=False)
            if fm:
                self.doc = doc
                return fm
