"""Put back the readings Python misaki keys by part of speech.

expand_dicts.py rewrote the gold dictionaries from eSpeak, one reading per
word, so heteronyms such as "present" and "separate" lost the readings
misaki gives each part of speech. This replaces the entry of every word
hexgrad/misaki (Apache-2.0) stores as a map with that map, taken at
UPSTREAM, writing misaki's one-letter diphthongs and affricates as the
joined pairs the rest of the dictionaries use.

Run from the repository root: python3 scripts/import_upstream_tags.py
"""

import json
import urllib.request

UPSTREAM = "fba1236595f2d2bf21d414ba6e57d25256afada3"
URL = "https://raw.githubusercontent.com/hexgrad/misaki/{}/misaki/data/{}_gold.json"

# misaki's letter for each sound, and the pair eSpeak writes for it.
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


def convert(phonemes, pairs):
    if phonemes is None:
        return None
    return "".join(pairs.get(c, c) for c in phonemes)


def main():
    for accent, pairs in PAIRS.items():
        with urllib.request.urlopen(URL.format(UPSTREAM, accent)) as response:
            upstream = json.load(response)
        path = f"data/{accent}_gold.json"
        with open(path, encoding="utf-8") as f:
            gold = json.load(f)
        maps = {w: v for w, v in upstream.items() if isinstance(v, dict)}
        already = sum(isinstance(gold.get(w), dict) for w in maps)
        for word, readings in maps.items():
            gold[word] = {tag: convert(ps, pairs) for tag, ps in readings.items()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(gold, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"{accent}: {len(maps)} maps, {already} of them maps already")


if __name__ == "__main__":
    main()
