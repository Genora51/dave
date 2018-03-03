from asyncio import subprocess, Queue
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
    # Give modules API access to nlp
    data["nlp"] = nlp
    return data


async def get_responses(generator):
    """List all responses from a module."""
    async for command, response in generator:
        finished = False
        while not finished:
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
                    # List: ['colour', HEXCOL(, CMD)]
                    sections = cmd.split(":")
                    if len(sections) >= 2:
                        # Get message type (CMD) if possible
                        form = sections[2]
                    else:
                        form = "msg"  # Default message type is plaintext
                    data = {
                        'form': form,
                        'colour': sections[1],
                        'message': response
                    }
                    yield "coloured reply", data
                elif cmd == "input":
                    inp = yield cmd, response
                    command, response = await generator.asend(inp)
                    yield
                    break
            else:
                finished = True


class InputRunner(object):
    """Manages running plugins."""

    def __init__(self, module_match):
        self.module_match = module_match
        self.inputs = Queue()
        self.running = False
        self.module = None

    def get_module(self, data):
        egg_name, egg_module = self.module_match.egg_match(data)
        if egg_name is not None:
            return get_responses(egg_module())
        module_name, module = self.module_match(data)
        m_data = extract_data(
            data, module_name,
            self.module_match, self.module_match.nlp
        )
        return get_responses(module(m_data))

    async def __call__(self, data):
        await self.inputs.put(data)
        if not self.running:
            self.running = True
            while not self.inputs.empty():
                if self.module is None:
                    self.module = self.get_module(await self.inputs.get())
                    if self.module is None:
                        continue
                else:
                    await self.module.asend(await self.inputs.get())
                async for reply in self.module:
                    if reply[0] == "input":
                        if reply[1] is not None:
                            yield "plaintext reply", reply[1]
                        self.running = False
                        return
                    else:
                        yield reply
                self.module = None
            self.running = False
