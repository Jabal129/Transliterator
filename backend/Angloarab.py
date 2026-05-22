# English → Arabized Script transliterator
# Requires: pip install pronouncing

try:
    import pronouncing
    _HAS_PRONOUNCING = True
except ImportError:
    _HAS_PRONOUNCING = False

import re

# ── Mini dictionary for offline demo ─────────────────────────────────────────
_MINI_CMU = {
    "comma":   ["K AA1 M AH0"],
    "hut":     ["HH AH1 T"],
    "hat":     ["HH AE1 T"],
    "hate":    ["HH EY1 T"],
    "heat":    ["HH IY1 T"],
    "hot":     ["HH AA1 T"],
    "hello":   ["HH AH0 L OW1"],
    "world":   ["W ER1 L D"],
    "python":  ["P AY1 TH AH0 N"],
    "apple":   ["AE1 P AH0 L"],
    "edit":    ["EH1 D AH0 T"],
    "open":    ["OW1 P AH0 N"],
    "unit":    ["Y UW1 N AH0 T"],
    "the":     ["DH AH0", "DH IY0"],
    "cat":     ["K AE1 T"],
    "bat":     ["B AE1 T"],
    "bit":     ["B IH1 T"],
    "boot":    ["B UW1 T"],
    "book":    ["B UH1 K"],
    "bird":    ["B ER1 D"],
    "boy":     ["B OY1"],
    "cow":     ["K AW1"],
    "bite":    ["B AY1 T"],
    "i":       ["AY1"],
    "a":       ["AH0", "EY1"],
    "is":      ["IH1 Z"],
    "it":      ["IH1 T"],
    "in":      ["IH0 N"],
    "on":      ["AO1 N", "AH0 N"],
    "and":     ["AE1 N D"],
    "this":    ["DH IH1 S"],
    "that":    ["DH AE1 T"],
    "with":    ["W IH1 DH"],
    "for":     ["F AO1 R"],
    "of":      ["AH1 V"],
    "to":      ["T UW1"],
    "have":    ["HH AE1 V"],
    "you":     ["Y UW1"],
    "he":      ["HH IY1"],
    "she":     ["SH IY1"],
    "we":      ["W IY1"],
    "they":    ["DH EY1"],
    "my":      ["M AY1"],
    "your":    ["Y AO1 R"],
    "from":    ["F R AH1 M"],
    "not":     ["N AA1 T"],
    "but":     ["B AH1 T"],
    "or":      ["AO1 R"],
    "an":      ["AE1 N"],
    "at":      ["AE1 T"],
    "be":      ["B IY1"],
    "do":      ["D UW1"],
    "go":      ["G OW1"],
    "so":      ["S OW1"],
    "no":      ["N OW1"],
    "me":      ["M IY1"],
    "was":     ["W AH1 Z"],
    "are":     ["AA1 R"],
    "can":     ["K AE1 N"],
    "will":    ["W IH1 L"],
    "one":     ["W AH1 N"],
    "two":     ["T UW1"],
    "three":   ["TH R IY1"],
    "four":    ["F AO1 R"],
    "five":    ["F AY1 V"],
    "six":     ["S IH1 K S"],
    "seven":   ["S EH1 V AH0 N"],
    "eight":   ["EY1 T"],
    "nine":    ["N AY1 N"],
    "ten":     ["T EH1 N"],
    "market":  ["M AA1 R K AH0 T"],
}

def _phones_for_word(word):
    if _HAS_PRONOUNCING:
        return pronouncing.phones_for_word(word)
    return _MINI_CMU.get(word.lower(), [])

# ── Mapping tables ────────────────────────────────────────────────────────────

CONSONANTS = {
    "B":  "ب",
    "CH": "چ",
    "D":  "د",
    "DH": "ذ",
    "F":  "ف",
    "G":  "غ",
    "HH": "ح",
    "JH": "ج",
    "K":  "ك",
    "L":  "ل",
    "M":  "م",
    "N":  "ن",
    "NG": "ڭ",
    "P":  "پ",
    "R":  "ر",
    "S":  "س",
    "SH": "ش",
    "T":  "ت",
    "TH": "ث",
    "V":  "ڤ",
    "W":  "و",
    "Y":  "ي",
    "Z":  "ز",
    "ZH": "ژ",
}

VOWELS = {
    "AA": ("آ",   "َا"),
    "AE": ("أَ",  "َ"),
    "AH": ("عَ",  "َ"),
    "AO": ("أو",  "ُو"),
    "AW": ("أَو", "َو"),
    "AY": ("أَي", "َي"),
    "EH": ("إِ",  "ِ"),
    "ER": ("عِر", "ِر"),
    "EY": ("إي",  "ِي"),
    "IH": ("إِ",  "ِ"),
    "IY": ("إي",  "ِي"),
    "OW": ("أو",  "ُو"),
    "OY": ("أوي", "ُوي"),
    "UH": ("أُ",  "ُ"),
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
            if is_first or not prev_was_consonant:
                result.append(initial)
            else:
                result.append(medial)
            prev_was_consonant = False
            is_first = False

        else:
            result.append(f"[{base}]")
            prev_was_consonant = False
            is_first = False

    return "".join(result)

# ── Punctuation handling ──────────────────────────────────────────────────────

# Splits a token into (leading_punct, word, trailing_punct)
# Word may contain apostrophes and hyphens (can't, well-known)
_PUNCT_RE = re.compile(r"^([^\w]*)([a-zA-Z][a-zA-Z'\-]*)([^\w]*)$")

def _split_token(token):
    """Return (pre_punct, word, post_punct) or (token, None, '') if no word."""
    m = _PUNCT_RE.match(token)
    if m:
        return m.group(1), m.group(2), m.group(3)
    return token, None, ""   # pure punctuation token (e.g. --, ...)

# ── Sentence transliterator ───────────────────────────────────────────────────

def transliterate_sentence(text):
    """
    Transliterate a full sentence to Arabized script.

    - Word order and spacing are preserved.
    - Only the first CMU pronunciation is used (direct transliteration).
    - Punctuation is detached from each word, the bare word is converted,
      then punctuation is re-attached at the same position.
    - Pure-punctuation tokens (e.g. --, ...) are passed through unchanged.
    - Unknown words are left in Latin script with a [?] marker.
    """
    tokens = text.split()
    output_tokens = []

    for token in tokens:
        pre, word, post = _split_token(token)

        if word is None:
            # Pure punctuation — pass through as-is
            output_tokens.append(pre)
            continue

        pronunciations = _phones_for_word(word)
        if pronunciations:
            arabic = phones_to_arabic(pronunciations[0])
            output_tokens.append(pre + arabic + post)
        else:
            output_tokens.append(pre + word + "[?]" + post)

    return " ".join(output_tokens)

# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mode = "pronouncing" if _HAS_PRONOUNCING else "built-in mini-dictionary"
    print(f"[Using {mode}]\n")

    sentences = [
        "intercontinental championship"
    ]

    for s in sentences:
        print(transliterate_sentence(s))