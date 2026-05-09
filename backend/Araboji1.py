"""
Araboji.py — Japanese → Romaji → Arabic transliteration.
"""

import unicodedata

import pandas as pd
from fugashi import Tagger
from pykakasi import kakasi


# ==========================
# 1️⃣ Load Excel Mapping
# ==========================

def load_mapping(excel_path: str) -> dict:
    df = pd.read_excel(excel_path)
    df = df.dropna(subset=["Romaji", "Arabic"])
    df["Romaji"] = df["Romaji"].astype(str).str.strip().str.lower()
    df["Arabic"] = df["Arabic"].astype(str).str.strip()
    return dict(zip(df["Romaji"], df["Arabic"]))


# ==========================
# 2️⃣ Japanese → Romaji
# ==========================

tagger = Tagger()
kks = kakasi()


def japanese_to_romaji(text: str) -> str:
    tokens = list(tagger(text))
    romaji_words = []
    i = 0

    while i < len(tokens):
        token = tokens[i]
        reading = token.feature.kana

        if reading:
            reading = unicodedata.normalize("NFKC", reading)

        # Case 1: No reading (punctuation, symbols, etc.) → keep surface form
        if reading is None:
            romaji_words.append(token.surface.lower())
            i += 1
            continue

        # Case 2: Token ends with small tsu → geminate the next consonant
        if reading.endswith(("っ", "ッ")) and i + 1 < len(tokens):
            next_token = tokens[i + 1]
            next_reading = next_token.feature.kana
            if next_reading:
                next_reading = unicodedata.normalize("NFKC", next_reading)
                combined = reading + next_reading
                converted = kks.convert(combined)
                romaji = "".join(item["hepburn"] for item in converted)
                romaji_words.append(romaji.lower())
                i += 2
                continue

        # Case 3: Merge standalone ん / ン with the preceding token
        if i + 1 < len(tokens):
            next_token = tokens[i + 1]
            next_reading = next_token.feature.kana
            if next_reading:
                next_reading = unicodedata.normalize("NFKC", next_reading)
                if next_reading in ("ん", "ン"):
                    combined = reading + next_reading
                    converted = kks.convert(combined)
                    romaji = "".join(item["hepburn"] for item in converted)
                    romaji_words.append(romaji.lower())
                    i += 2
                    continue

        # Default: convert current token alone
        converted = kks.convert(reading)
        romaji = "".join(item["hepburn"] for item in converted)
        romaji_words.append(romaji.lower())
        i += 1

    return " ".join(romaji_words)


# ==========================
# 3️⃣ Romaji → Arabic
# ==========================

def arabize_romaji(romaji_text: str, mapping: dict) -> str:
    VOWELS = ("a", "i", "u", "e", "o")
    keys = sorted(mapping.keys(), key=len, reverse=True)  # longest-match first
    result_words = []

    for word in romaji_text.split():
        i = len(word) - 1
        arabic_word = ""

        while i >= 0:
            matched = False

            for key in keys:
                start = i - len(key) + 1
                if start < 0:
                    continue

                segment = word[start : i + 1]

                # Standalone 'n': don't consume it if followed by a vowel or 'y'
                if key == "n":
                    next_pos = start + 1
                    if next_pos < len(word) and (
                        word[next_pos] in VOWELS or word[next_pos] == "y"
                    ):
                        continue

                if segment == key:
                    arabic_word = mapping[key] + arabic_word
                    i -= len(key)
                    matched = True
                    break

            if not matched:
                arabic_word = word[i] + arabic_word
                i -= 1

        result_words.append(arabic_word)

    return " ".join(result_words)


# ==========================
# 4️⃣ Full Pipeline
# ==========================

def japanese_to_arabic(text: str, mapping: dict) -> tuple[str, str]:
    """Return (romaji, arabic) for the given Japanese text."""
    romaji = japanese_to_romaji(text)
    arabic = arabize_romaji(romaji, mapping)
    return romaji, arabic