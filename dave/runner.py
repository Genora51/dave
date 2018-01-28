def extract_data(text, name, matcher, nlp):
    data = {}
    data["text"] = text
    data["alias"] = name
    if hasattr(matcher, "doc"):
        data["doc"] = matcher.doc
    else:
        data["doc"] = nlp(text)
    return data


def run_module(module, data):
    yield from module(data)
