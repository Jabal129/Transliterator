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

def load_mapping(excel_path):
    df = pd.read_excel(excel_path)

    # Remove empty rows
    df = df.dropna(subset=["Romaji", "Arabic"])

    # Convert to string and strip spaces
    df["Romaji"] = df["Romaji"].astype(str).str.strip().str.lower()
    df["Arabic"] = df["Arabic"].astype(str).str.strip()

    mapping = dict(zip(df["Romaji"], df["Arabic"]))
    return mapping


# ==========================
# 2️⃣ Japanese → Romaji
# ==========================

tagger = Tagger()
kks = kakasi()

def japanese_to_romaji(text):
    tokens = list(tagger(text))
    romaji_words = []
    i = 0

    while i < len(tokens):
        token = tokens[i]
        reading = token.feature.kana

        # Normalize reading to avoid script or encoding issues
        if reading:
            reading = unicodedata.normalize('NFKC', reading)

        # Case 1: No reading (punctuation, symbols, etc.) → keep surface form
        if reading is None:
            romaji_words.append(token.surface.lower())
            i += 1
            continue

        # Case 2: Current token ends with small tsu (either hiragana or katakana)
        if reading.endswith(('っ', 'ッ')) and i + 1 < len(tokens):
            next_token = tokens[i + 1]
            next_reading = next_token.feature.kana
            if next_reading:
                next_reading = unicodedata.normalize('NFKC', next_reading)
                combined = reading + next_reading
                converted = kks.convert(combined)
                romaji = "".join([item['hepburn'] for item in converted])
                romaji_words.append(romaji.lower())
                i += 2  # Skip next token
                continue

        # Case 3: Next token is standalone ん (hiragana or katakana)
        if i + 1 < len(tokens):
            next_token = tokens[i + 1]
            next_reading = next_token.feature.kana
            if next_reading:
                next_reading = unicodedata.normalize('NFKC', next_reading)
                if next_reading in ('ん', 'ン'):
                    combined = reading + next_reading
                    converted = kks.convert(combined)
                    romaji = "".join([item['hepburn'] for item in converted])
                    romaji_words.append(romaji.lower())
                    i += 2
                    continue

        # Default: convert current token alone
        converted = kks.convert(reading)
        romaji = "".join([item['hepburn'] for item in converted])
        romaji_words.append(romaji.lower())
        i += 1

    return " ".join(romaji_words)


# ==========================
# 3️⃣ Romaji → Arabic
# ==========================

def arabize_romaji(romaji_text, mapping):
    result_words = []

    # Sort keys by length descending for longest match first
    keys = sorted(mapping.keys(), key=len, reverse=True)
    vowels = ("a", "i", "u", "e", "o")

    # Split by spaces to handle word-by-word
    words = romaji_text.split(" ")

    for word in words:
        i = len(word) - 1  # Start from last letter
        arabic_word = ""

        while i >= 0:
            matched = False

            for key in keys:
                start = i - len(key) + 1
                if start < 0:
                    continue
                segment = word[start:i+1]

                # Handle standalone 'n' correctly
                if key == "n":
                    if start + 1 < len(word) and (word[start+1] in vowels or word[start+1] == 'y'):
                        continue

                if segment == key:
                    arabic_word = mapping[key] + arabic_word  # prepend since we're moving backward
                    i -= len(key)
                    matched = True
                    break

            if not matched:
                # keep unknown chars
                arabic_word = word[i] + arabic_word
                i -= 1

        result_words.append(arabic_word)

    return " ".join(result_words)


# ==========================
# 4️⃣ Full Pipeline
# ==========================

def japanese_to_arabic(text, mapping):
    romaji = japanese_to_romaji(text)
    arabic = arabize_romaji(romaji, mapping)
    return romaji, arabic