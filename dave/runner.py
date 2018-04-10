from asyncio import subprocess, Queue
import shlex


def extract_data(text, name, matcher, nlp):
    """Create a data dict for DAVE plugins to use."""
    data = {}
    data["text"] = text
    data["alias"] = name
    # Use already-run NLP if possible, to increase efficiency
    if hasattr(matcher, "doc") and matcher.doc is not None:
        data["doc"] = matcher.doc
    else:
        data["doc"] = nlp(matcher.first_lower(text))
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


async def say(text, voice="Daniel"):
    # Builtin MacOS `say` command for TTS
    proc = await subprocess.create_subprocess_exec(
        "say", "-v", voice, text
    )
    await proc.wait()


def make_async(coro):
    """Converts synchronous to asynchronous generators."""
    if hasattr(coro, "__aiter__"):
        # Already async, no changes
        return coro
    else:
        async def agen():
            r = coro.send(None)  # prime the coro
            while True:
                try:
                    try:
                        x = yield r
                    except Exception as e:
                        r = coro.throw(e)
                    else:
                        r = coro.send(x)
                except StopIteration:
                    break
        return agen()


async def get_responses(coro):
    """List all responses from a module."""
    generator = make_async(coro)
    async for command, response in generator:
        finished = False
        while not finished:
            # List of commands (message types)
            cmds = command.split("; ")
            for cmd in cmds:
                if cmd.startswith("say"):
                    opts = cmd.split(":")
                    if len(opts) > 1:
                        await say(response, voice=opts[1])
                    else:
                        await say(response)
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
                    try:
                        command, response = await generator.asend(inp)
                        yield
                        break
                    except StopAsyncIteration:
                        yield
            else:
                finished = True


class InputRunner(object):
    """Manages running plugins."""

    def __init__(self, module_match):
        # Initialise object variables
        self.module_match = module_match
        # Input queue for premature input
        self.inputs = Queue()
        # Is a module currently in process?
        self.running = False
        # Which module is currently being iterated?
        self.module = None

    def get_module(self, data):
        # Is there a matching easter egg?
        egg_name, egg_module = self.module_match.egg_match(data)
        # If found, return that plugin's iterable
        if egg_name is not None:
            return get_responses(egg_module())
        # Attempts to match against a plugin
        module_name, module = self.module_match(data)
        # Extract input data
        m_data = extract_data(
            data, module_name,
            self.module_match, self.module_match.nlp
        )
        if module_name is None:
            module = self.module_match.fallback
        if module is not None:
            # Returns that plugin's iterable too.
            return get_responses(module(m_data))
        else:
            return None

    async def __call__(self, data):
        # Add this input to the queue
        await self.inputs.put(data)
        # Make sure that nothing is already running
        if not self.running:
            self.running = True  # Now it is running
            # Iterate until inputs run out
            while not self.inputs.empty():
                # If no current module, matches against a new one
                if self.module is None:
                    self.module = self.get_module(await self.inputs.get())
                    if self.module is None:  # No match
                        continue
                else:  # Input must have been requested
                    await self.module.asend(await self.inputs.get())
                # Iterate through the plugin
                try:
                    async for reply in self.module:
                        if reply[0] == "input":
                            # Break on input request (waits until new input)
                            if reply[1] is not None:
                                yield "plaintext reply", reply[1]
                                await say(reply[1])
                            break
                        else:
                            # Normal case: emit to client
                            yield reply
                    else:
                        # Once a module has stopped
                        self.module_match.doc = None
                        self.module = None
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    # An error in the plugin has occurred
                    msg = "Sorry, something went wrong there."
                    # Send message to user
                    yield "plaintext reply", msg
                    await say(msg)
                    # Reset module
                    self.module_match.doc = None
                    self.module = None
            # Finished, so no longer running
            self.running = False
