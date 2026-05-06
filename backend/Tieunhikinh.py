from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import re

def transliterate_vietnamese_to_arabic(sentence):
    # Mappings for consonants, vowels, and tones
    consonants_mapping = {
        "ngh": "غّ", "ng": "غّ", "ch": "جّ", "nh": "نّ", "ph": "ف", "th": "ت", "tr": "تّ", "gh": "غ", "kh": "خ", "gi": "ج",
        "b": "ب", "c": "ك", "k": "ك", "q": "ك", "d": "ذ", "đ": "د", "g": "غ", "h": "ھ", "l": "ل", "m": "م", "n": "ن", 
        "p": "بّ", "r": "ر", "s": "ش", "t": "ط", "v": "و", "x": "س"
    }

    vowels_mapping = {
        "ă": "َ", "a": "َ", "ơ": "ً", "â": "ً", "ê": "َا", "e": "ًا", "i": "ِ", "y": "ِ", "ư": "ٍ", 
        "u": "ُو", "ô": "ُ", "o": "ٌ", "oe": "ُوًا", "ue": "ُوًا", "uê": "ُوَا", "uy": "ُوِ", "uyê": "ُوِيَا", 
        "uya": "ُوِيَا", "oa": "ُوَ", "ua": "ُوَ", "oă": "ُوَ", "uă": "ُوَ", "uâ": "ُوً", "uơ": "ُوً", 
        "oeo": "ُوًاو", "ueo": "ُوًاو", "uyu": "ُوِو", "oai": "ُوَي", "uai": "ُوَي", "oao": "ُوَو", "uao": "ُوَو", 
        "oay": "ُوَي", "uay": "ُوَي", "uây": "ُوًي", "ai": "َي", "ay": "َي", "ây": "ًي", "ơi": "ًي", 
        "ưi": "ٍي", "ươi": "ٍيًي", "oi": "ٌي", "ôi": "ُي", "ui": "ُوي", "uôi": "ُووًي", "eo": "ًاو", 
        "êu": "َاو", "iu": "ِو", "iêu": "ِيًو", "yêu": "ِيًو", "ao": "َو", "au": "َو", "âu": "ًو", 
        "ơu": "ًو", "ưu": "ٍو", "ươu": "ٍيًو", "iê": "ِيَا", "ươ": "ٍيً", "uô": "ُووُ", "oo": "ٌ", "ôô": "ُ"
    }

    tone_mapping = {
        "1": "۱", "2": "۲", "3": "۳", "4": "٤", "5": "٥"
    }

    # Normalize vowels by removing tone diacritics
    vowel_diacritics_map = {
        "á": "a", "à": "a", "ả": "a", "ã": "a", "ạ": "a",
        "ắ": "ă", "ằ": "ă", "ẳ": "ă", "ẵ": "ă", "ặ": "ă",
        "ấ": "â", "ầ": "â", "ẩ": "â", "ẫ": "â", "ậ": "â",
        "é": "e", "è": "e", "ẻ": "e", "ẽ": "e", "ẹ": "e",
        "ế": "ê", "ề": "ê", "ể": "ê", "ễ": "ê", "ệ": "ê",
        "í": "i", "ì": "i", "ỉ": "i", "ĩ": "i", "ị": "i",
        "ó": "o", "ò": "o", "ỏ": "o", "õ": "o", "ọ": "o",
        "ố": "ô", "ồ": "ô", "ổ": "ô", "ỗ": "ô", "ộ": "ô",
        "ớ": "ơ", "ờ": "ơ", "ở": "ơ", "ỡ": "ơ", "ợ": "ơ",
        "ú": "u", "ù": "u", "ủ": "u", "ũ": "u", "ụ": "u",
        "ứ": "ư", "ừ": "ư", "ử": "ư", "ữ": "ư", "ự": "ư",
        "ý": "y", "ỳ": "y", "ỷ": "y", "ỹ": "y", "ỵ": "y"
    }

    tone_indicator_map = {
        "á": "۱", "ắ": "۱", "ấ": "۱", "é": "۱", "ế": "۱", "í": "۱", "ó": "۱", "ố": "۱", "ớ": "۱", "ú": "۱", "ứ": "۱", "ý": "۱",
        "à": "۲", "ằ": "۲", "ầ": "۲", "è": "۲", "ề": "۲", "ì": "۲", "ò": "۲", "ồ": "۲", "ờ": "۲", "ù": "۲", "ừ": "۲", "ỳ": "۲",
        "ả": "۳", "ẳ": "۳", "ẩ": "۳", "ẻ": "۳", "ể": "۳", "ỉ": "۳", "ỏ": "۳", "ổ": "۳", "ở": "۳", "ủ": "۳", "ử": "۳", "ỷ": "۳",
        "ã": "٤", "ẵ": "٤", "ẫ": "٤", "ẽ": "٤", "ễ": "٤", "ĩ": "٤", "õ": "٤", "ỗ": "٤", "ỡ": "٤", "ũ": "٤", "ữ": "٤", "ỹ": "٤",
        "ạ": "٥", "ặ": "٥", "ậ": "٥", "ẹ": "٥", "ệ": "٥", "ị": "٥", "ọ": "٥", "ộ": "٥", "ợ": "٥", "ụ": "٥", "ự": "٥", "ỵ": "٥"
    }

    def transliterate_word(word):
        # Normalize vowels by removing tone diacritics
        tone = ""
        for accented_vowel, normalized_vowel in vowel_diacritics_map.items():
            if accented_vowel in word:
                word = word.replace(accented_vowel, normalized_vowel)
                tone = tone_indicator_map.get(accented_vowel, "")

        # Identify vowel nucleus (triphthongs > diphthongs > single vowels)
        vowel_nucleus = ""
        for vowel_combo in sorted(vowels_mapping.keys(), key=len, reverse=True):
            if vowel_combo in word:
                vowel_nucleus = vowel_combo
                break

        # Perform transliteration
        arabic_translit = ""
        index = 0
        while index < len(word):
            match = False

            # Check for digraph consonant match first
            for digraph in [k for k in consonants_mapping.keys() if len(k) > 1]:
                if word[index:].startswith(digraph):
                    arabic_translit += consonants_mapping[digraph]
                    index += len(digraph)
                    match = True
                    break

            # Check for single consonant match
            if not match:
                for consonant in [k for k in consonants_mapping.keys() if len(k) == 1]:
                    if word[index:].startswith(consonant):
                        arabic_translit += consonants_mapping[consonant]
                        index += len(consonant)
                        match = True
                        break

            # Check for vowel nucleus match
            if not match and vowel_nucleus and word[index:].startswith(vowel_nucleus):
                arabic_translit += vowels_mapping[vowel_nucleus]
                index += len(vowel_nucleus)
                match = True

            # Move to the next character if no match
            if not match:
                index += 1

        # Append tone if available
        arabic_translit += tone

        # Add Alif if the word doesn't begin with a consonant
        if arabic_translit and arabic_translit[0] not in consonants_mapping.values():
            arabic_translit = 'ا' + arabic_translit

        return arabic_translit

    # Split the sentence into words and process each
    words = sentence.split()
    transliterated_words = []
    for word in words:
        # Preserve original capitalization
        is_capitalized = word[0].isupper()
        transliterated_word = transliterate_word(word.lower())
        if is_capitalized:
            transliterated_word = transliterated_word.capitalize()
        transliterated_words.append(transliterated_word)

    # Join words back with spaces
    return ' '.join(transliterated_words)