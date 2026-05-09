import re
import pandas as pd
from pykakasi import kakasi
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import nest_asyncio
import asyncio
import unicodedata
from punctuation_helper import preserve_and_process

try:
    from fugashi import Tagger
except ModuleNotFoundError:
    Tagger = None

_tagger = None


def get_tagger():
    global _tagger
    if Tagger is None:
        raise ModuleNotFoundError(
            "fugashi is required for Japanese transliteration. Install fugashi in the environment."
        )
    if _tagger is None:
        _tagger = Tagger()
    return _tagger


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

    def is_arabic_text(value):
        return any(
            0x0600 <= ord(ch) <= 0x06FF or
            0x0750 <= ord(ch) <= 0x077F or
            0x08A0 <= ord(ch) <= 0x08FF
            for ch in value
        )

    mapping = {}
    for romaji, arabic in zip(df["Romaji"], df["Arabic"]):
        if not romaji:
            continue
        if romaji not in mapping or not is_arabic_text(mapping[romaji]):
            if is_arabic_text(arabic):
                mapping[romaji] = arabic

    return mapping


# ==========================
# 2️⃣ Japanese → Romaji
# ==========================



kks = kakasi()


def japanese_to_romaji(text):
    tagger = get_tagger()
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

def japanese_to_arabic_word(japanese_word, mapping):
    """Convert a single Japanese word (no punctuation) to Arabic."""
    romaji = japanese_to_romaji(japanese_word)
    arabic = arabize_romaji(romaji, mapping)
    arabic = re.sub(r"n(?=[\u064B-\u0652])", "ن", arabic)
    return arabic


def japanese_to_arabic(text, mapping):
    """Convert Japanese text to Arabic while preserving punctuation."""
    def process_word(word):
        return japanese_to_arabic_word(word, mapping)
    
    return preserve_and_process(text, process_word)


# ==========================
# 🤖 BOT HANDLERS
# ==========================

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Welcome! Send me Japanese text and I'll transliterate it to Arabic."
    )


async def convert(update: Update, context: CallbackContext):
    japanese_text = update.message.text

    _, arabic = japanese_to_arabic(japanese_text)

    await update.message.reply_text(arabic)



async def main():
    application = Application.builder().token("8303958701:AAGE3xPmnKgHLVRt4D15PAqscXYHBOisohs").build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert))

    await application.run_polling()


# ==========================
# Run Bot
# ==========================

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
