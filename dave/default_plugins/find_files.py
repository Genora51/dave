import subprocess
from fuzzywuzzy import process, fuzz
from os import path
from googleapiclient.discovery import build
import webbrowser


def base_no_ext(pth):
    return path.splitext(path.basename(pth))[0]


class AppOpener:
    def __init__(self, data):
        self.data = data
        self.cse = build(
            "customsearch", "v1",
            developerKey="AIzaSyDpwQVbWUMpAH1dcXZZ-iwxqiDTuUrpTSk"
        ).cse()

    def __iter__(self):
        proc = subprocess.Popen(
            ['mdfind', '-onlyin', '/', 'kMDItemKind=="Application"'],
            stdout=subprocess.PIPE
        )
        apps = proc.communicate()[0].decode("utf-8").splitlines()
        apps_rem = list(map(base_no_ext, apps))
        proc.terminate()
        query = " ".join(t.orth_ for t in self.data["keywords"])
        best_app = process.extractOne(
            query, apps_rem,
            score_cutoff=75
        )
        if best_app is not None:
            ba = apps[apps_rem.index(best_app[0])]
            yield "msg; say", "Opening {}.".format(best_app[0])
            subprocess.call(["open", ba])
        else:
            results = self.cse.list(
                q=query, cx="015857082664601314423:5a9surbczss"
            ).execute()
            result = results["items"][0]
            yield "msg; say", "Opening {}.".format(result["title"])
            webbrowser.open(result["link"])


def setup(app):
    ao_aliases = ["open", "run", "start", "launch"]
    app.register_aliases(ao_aliases, AppOpener)
