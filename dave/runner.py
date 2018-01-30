import subprocess
import shlex


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
    for command, response in module(data):
        cmds = command.split("; ")
        for cmd in cmds:
            if cmd == "say":
                subprocess.Popen([
                    "say", "-v", "Daniel",
                    shlex.quote(response)
                ])
            elif cmd == "msg":
                yield "plaintext reply", response
            elif cmd == "html":
                yield "html reply", response
            elif cmd.startswith("colour:"):
                sections = cmd.split(":")
                if len(sections) >= 2:
                    form = sections[2]
                else:
                    form = "msg"
                data = {
                    'form': form,
                    'colour': sections[1],
                    'message': response
                }
                yield "coloured reply", data
