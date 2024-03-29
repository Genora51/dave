from asyncio import subprocess
from fuzzywuzzy import process, fuzz
from os import path
from googleapiclient.discovery import build
import webbrowser


def base_no_ext(pth):
    """Get base name of a file w/o extension."""
    return path.splitext(path.basename(pth))[0]


class AppOpener:
    def __init__(self, data):
        self.data = data

    async def __aiter__(self):
        # Get list of applications
        proc = await subprocess.create_subprocess_exec(
            'mdfind', '-onlyin', '/', 'kMDItemKind=="Application"',
            stdout=subprocess.PIPE
        )
        apps_l = await proc.communicate()
        apps = apps_l[0].decode("utf-8").splitlines()
        # Get base names using base_no_ext()
        apps_rem = list(map(base_no_ext, apps))
        # Get desired app name from keywords
        query = " ".join(t.orth_ for t in self.data["keywords"])
        # Attempt best match
        best_app = process.extractOne(
            query, apps_rem,
            score_cutoff=75
        )
        if best_app is not None:  # If match, reply and open
            ba = apps[apps_rem.index(best_app[0])]
            yield "msg; say", "Opening {}.".format(best_app[0])
            pc = await subprocess.create_subprocess_exec("open", ba)
            await pc.wait()
        else:
            # Build google custom search engine
            self.cse = build(
                "customsearch", "v1",
                developerKey="AIzaSyDpwQVbWUMpAH1dcXZZ-iwxqiDTuUrpTSk"
            ).cse()
            # Otherwise, get top Google result
            results = self.cse.list(
                q=query, cx="015857082664601314423:5a9surbczss"
            ).execute()
            result = results["items"][0]
            # Reply and open in browser
            yield "msg; say", "Opening {}.".format(result["title"])
            webbrowser.open(result["link"])


class FileFinder:
    def __init__(self, data):
        self.data = data

    async def __aiter__(self):
        # Create MacOS `mdfind` query from keywords
        kws = "*".join(t.orth_ for t in self.data["keywords"])
        query = "kMDItemDisplayName=='*{}*'cdw".format(kws)
        # Execute query and get list of matches
        proc = await subprocess.create_subprocess_exec(
            'mdfind', query, stdout=subprocess.PIPE
        )
        result_l = await proc.communicate()
        result = result_l[0].decode("utf-8").splitlines()
        if len(result) > 0:
            # Reply and open file in Finder
            found = result[0]
            name = path.basename(found)
            yield "msg", "Located {}.".format(name)
            yield "say", "Located {}.".format(name.replace(".", " dot "))
            pc = await subprocess.create_subprocess_exec("open", "-R", found)
            await pc.wait()
        else:
            yield "msg; say", "I couldn't find that file."


def setup(app):
    ao_aliases = ["open", "run", "start", "launch"]
    app.register_aliases(ao_aliases, AppOpener)
    ff_aliases = ["find", "locate"]
    app.register_aliases(ff_aliases, FileFinder)
