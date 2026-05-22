# English → Arabized Script transliterator
# Requires: pip install pronouncing
# OR: run once with internet to auto-download the CMU dict (~4MB, cached locally)

import re
import os

# ── Mini fallback dictionary (defined first so _build_dict can reference it) ─

_MINI_CMU = {
    "big":     ["B IH1 G"],
    "small":   ["S M AO1 L"],
    "comma":   ["K AA1 M AH0"],
    "hut":     ["HH AH1 T"],
    "hat":     ["HH AE1 T"],
    "hate":    ["HH EY1 T"],
    "heat":    ["HH IY1 T"],
    "hot":     ["HH AA1 T"],
    "hello":   ["HH AH0 L OW1"],
    "world":   ["W ER1 L D"],
    "the":     ["DH AH0", "DH IY0"],
    "a":       ["AH0", "EY1"],
    "i":       ["AY1"],
    "is":      ["IH1 Z"],
    "and":     ["AE1 N D"],
    "she":     ["SH IY1"],
    "my":      ["M AY1"],
    "can":     ["K AE1 N"],
    "you":     ["Y UW1"],
    "go":      ["G OW1"],
    "to":      ["T UW1"],
    "have":    ["HH AE1 V"],
    "cat":     ["K AE1 T"],
    "bird":    ["B ER1 D"],
    "open":    ["OW1 P AH0 N"],
    "market":  ["M AA1 R K AH0 T"],
    "one":     ["W AH1 N"],
    "two":     ["T UW1"],
    "three":   ["TH R IY1"],
}

# ── CMU dictionary loader (runs once at import time) ──────────────────────────

_CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cmudict.txt")
_CMU_URL    = "https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict"

def _parse_cmudict_file(path):
    d = {}
    with open(path, encoding="latin-1") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(";;;"):
                continue
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            key = re.sub(r'\(\d+\)$', '', parts[0]).lower()
            d.setdefault(key, []).append(parts[1].strip())
    return d

def _build_dict():
    # 1. pronouncing + g2p fallback
    try:
        import pronouncing
        from g2p_en import G2p

        g2p = G2p()

        def lookup(word):
            word = word.lower()

            # First try CMUdict
            phones = pronouncing.phones_for_word(word)

            if phones:
                return phones

            # Fallback: predict pronunciation
            predicted = " ".join(g2p(word))

            print(f"[G2P fallback] {word} -> {predicted}")

            return [predicted]

        print("[CMU: using 'pronouncing' + g2p fallback]")
        return lookup

    except ImportError:
        pass

    # 2. locally cached plain-text CMU dict file
    if os.path.exists(_CACHE_PATH):
        d = _parse_cmudict_file(_CACHE_PATH)
        print(f"[CMU: loaded from cache ({len(d):,} entries)]")
        return d.get

    # 3. auto-download once, then cache
    try:
        import urllib.request
        print(f"[CMU: downloading dict → {_CACHE_PATH} ...]")
        urllib.request.urlretrieve(_CMU_URL, _CACHE_PATH)
        d = _parse_cmudict_file(_CACHE_PATH)
        print(f"[CMU: downloaded and cached ({len(d):,} entries)]")
        return d.get
    except Exception as e:
        print(f"[CMU: download failed ({e})]")

    # 4. built-in mini-dict as last resort
    print("[CMU: WARNING — using mini-dictionary. Install 'pronouncing' for full coverage.]")
    return _MINI_CMU.get

# Build once at import time
_lookup = _build_dict()

def _phones_for_word(word):
    result = _lookup(word.lower())
    return result if result else []

# ── Mapping tables ────────────────────────────────────────────────────────────

CONSONANTS = {
    "B":  "ب",  "CH": "چ",  "D":  "د",  "DH": "ذ",
    "F":  "ف",  "G":  "گ",  "HH": "ه",  "JH": "ج",
    "K":  "ک",  "L":  "ل",  "M":  "م",  "N":  "ن",
    "NG": "ݣ",  "P":  "پ",  "R":  "ر",  "S":  "س",
    "SH": "ش",  "T":  "ت",  "TH": "ث",  "V":  "ڤ",
    "W":  "و",  "Y":  "ي",  "Z":  "ز",  "ZH": "ژ",
}

VOWELS = {
    "AA": ("آ",   "َا"),   "AE": ("أَ",  "َ"),
    "AH": ("عَ",  "َ"),    "AO": ("أو",  "ُو"),
    "AW": ("أَو", "َو"),   "AY": ("أَي", "َي"),
    "EH": ("إِ",  "ِ"),    "ER": ("عِر", "ِر"),
    "EY": ("إي",  "ِي"),   "IH": ("إِ",  "ِ"),
    "IY": ("إي",  "ِي"),   "OW": ("أو",  "ُو"),
    "OY": ("أوي", "ُوي"),  "UH": ("أُ",  "ُ"),
    "UW": ("أُو", "ُو"),
}

# ── Core phoneme converter ────────────────────────────────────────────────────

def strip_stress(phone):
    return phone.rstrip("012")

def phones_to_arabic(phones_str):
    phones = phones_str.split()
    result = []
    prev_was_consonant = False
    is_first = True

    for phone in phones:
        base = strip_stress(phone)
        if base in CONSONANTS:
            result.append(CONSONANTS[base])
            prev_was_consonant = True
            is_first = False
        elif base in VOWELS:
            initial, medial = VOWELS[base]
            result.append(initial if (is_first or not prev_was_consonant) else medial)
            prev_was_consonant = False
            is_first = False
        else:
            result.append(f"[{base}]")
            prev_was_consonant = False
            is_first = False

    return "".join(result)

# ── Punctuation handling ──────────────────────────────────────────────────────

_PUNCT_RE = re.compile(r"^([^\w]*)([a-zA-Z][a-zA-Z'\-]*)([^\w]*)$")

def _split_token(token):
    m = _PUNCT_RE.match(token)
    if m:
        return m.group(1), m.group(2), m.group(3)
    return token, None, ""

# ── Sentence transliterator ───────────────────────────────────────────────────

def transliterate_sentence(text):
    tokens = text.split()
    output_tokens = []
    for token in tokens:
        pre, word, post = _split_token(token)
        if word is None:
            output_tokens.append(pre)
            continue
        pronunciations = _phones_for_word(word)
        if pronunciations:
            output_tokens.append(pre + phones_to_arabic(pronunciations[0]) + post)
        else:
            output_tokens.append(pre + word + "[?]" + post)
    return " ".join(output_tokens)

# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    sentences = [
        "comma hut hat hate heat hot",
        "Hello, world!",
        "I have a big cat, and she is my bird.",
        "Can you go to the open market?",
        "One, two, three -- go!",
    ]
    for s in sentences:
        print(f"EN: {s}")
        print(f"AR: {transliterate_sentence(s)}")
        print()