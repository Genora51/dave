def extract_data(text, name, matcher, nlp):
    data = {}
    data["text"] = text
    data["alias"] = name
    if hasattr(matcher, "doc"):
        data["doc"] = matcher.doc
    else:
        data["doc"] = nlp(text)
    doc = data["doc"]
    keywords = (t for t in doc
                if not t.is_stop | t.is_punct | t.is_space)
    stops = [
        "tell", "show", "dave", "please",
        "like", "want", "could", data["alias"]
    ]
    data["keywords"] = list(filter(lambda x: x.lemma_ not in stops, keywords))
    return data


def run_module(module, data):
    yield from module(data)
