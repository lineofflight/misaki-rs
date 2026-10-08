"""Build data/ as a hybrid of Python misaki's dictionaries and eSpeak-ng's.

Every word hexgrad/misaki (Apache-2.0) has takes misaki's entry and tier,
gold or silver, at UPSTREAM: a reading, or a map of readings by part of
speech. Only the notation changes: misaki's one-letter diphthongs and
affricates become the joined pairs the eSpeak-ng entries use. Every other
word keeps the entry expand_dicts.py generated with eSpeak-ng, as
committed at ESPEAK.

The eSpeak-ng entries are read from git history and misaki's fetched at a
pinned commit, never from the files this writes, so running it again
gives the same data.

Run from the repository root: python3 scripts/build_hybrid_dictionary.py
"""

import json
import subprocess

# hexgrad/misaki, where misaki/data last changed.
UPSTREAM = "e820629b96334db28227df37f280e4836d46fadb"
URL = "https://raw.githubusercontent.com/hexgrad/misaki/{}/misaki/data/{}.json"
# This repository, where expand_dicts.py last wrote data/.
ESPEAK = "3ab12e5f46934bbdd376222980b95128eca28131"

# misaki's letter for each sound, and the pair eSpeak-ng writes for it,
# joined by U+200D.
SHARED = {
    "A": "e‍ɪ",
    "I": "a‍ɪ",
    "W": "a‍ʊ",
    "Y": "ɔ‍ɪ",
    "ʤ": "d‍ʒ",
    "ʧ": "t‍ʃ",
}
PAIRS = {
    "gb": {**SHARED, "Q": "ə‍ʊ"},
    "us": {**SHARED, "O": "o‍ʊ"},
}


def run(*command):
    return subprocess.run(command, capture_output=True, check=True).stdout


def espeak(name):
    return json.loads(run("git", "show", f"{ESPEAK}:data/{name}.json"))


def upstream(name):
    return json.loads(run("curl", "-fsSL", URL.format(UPSTREAM, name)))


def convert(entry, pairs):
    if entry is None:
        return None
    if isinstance(entry, dict):
        return {tag: convert(ps, pairs) for tag, ps in entry.items()}
    return "".join(pairs.get(c, c) for c in entry)


def main():
    for accent, pairs in PAIRS.items():
        tiers = [f"{accent}_gold", f"{accent}_silver"]
        misaki = {
            name: {word: convert(entry, pairs) for word, entry in upstream(name).items()}
            for name in tiers
        }
        known = set().union(*misaki.values())
        for name in tiers:
            kept = {word: entry for word, entry in espeak(name).items() if word not in known}
            with open(f"data/{name}.json", "w", encoding="utf-8") as f:
                json.dump(
                    {**kept, **misaki[name]},
                    f,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
            maps = sum(isinstance(entry, dict) for entry in misaki[name].values())
            print(
                f"{name}: {len(misaki[name])} from misaki ({maps} by part of speech), "
                f"{len(kept)} from eSpeak-ng"
            )


if __name__ == "__main__":
    main()
