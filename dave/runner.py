from asyncio import subprocess
import shlex


def extract_data(text, name, matcher, nlp):
    """Create a data dict for DAVE plugins to use."""
    data = {}
    data["text"] = text
    data["alias"] = name
    # Use already-run NLP if possible, to increase efficiency
    if hasattr(matcher, "doc"):
        data["doc"] = matcher.doc
    else:
        data["doc"] = nlp(text)
    doc = data["doc"]
    # Extract "keywords" from the NLP object
    keywords = (t for t in doc
                if not t.is_stop | t.is_punct | t.is_space)
    # Filter for DAVE-specific stopwords, including module alias
    stops = [
        "tell", "show", "dave", "please",
        "like", "want", "could", data["alias"]
    ]
    data["keywords"] = list(filter(lambda x: x.lemma_ not in stops, keywords))
    return data


async def get_responses(generator):
    """List all responses from a module."""
    async for command, response in generator:
        # List of commands (message types)
        cmds = command.split("; ")
        for cmd in cmds:
            if cmd.startswith("say"):
                opts = cmd.split(":")
                if len(opts) > 1:
                    voice = opts[1]
                else:
                    voice = "Daniel"
                # Builtin MacOS `say` command for TTS
                proc = await subprocess.create_subprocess_exec(
                    "say", "-v", voice, response
                )
                await proc.wait()
            elif cmd == "msg":
                yield "plaintext reply", response
            elif cmd == "html":
                yield "html reply", response
            # Coloured response; syntax is colour:#HEXCOL(:CMD)
            elif cmd.startswith("colour:"):
                sections = cmd.split(":")  # List: ['colour', HEXCOL(, CMD)]
                if len(sections) >= 2:
                    form = sections[2]  # Get message type (CMD) if possible
                else:
                    form = "msg"  # Default message type is plaintext
                data = {
                    'form': form,
                    'colour': sections[1],
                    'message': response
                }
                yield "coloured reply", data


async def run_module(module, data):
    """Convert module data to UI messages."""
    async for reply in get_responses(module(data)):
        yield reply


async def run_egg(egg_module):
    async for reply in get_responses(egg_module()):
        yield reply
