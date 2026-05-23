# Russian (Cyrillic) → Arabized Script transliterator
# Based on the provided Arabic-script mapping guide

import re

# ── Mapping tables ────────────────────────────────────────────────────────────
# Each Cyrillic letter maps to (initial_form, medial_form)
# For consonants: both forms are the same letter
# For vowels: initial = full letter (word-start or after another vowel)
#             medial  = diacritic form (after a consonant)
# Soft sign Ь palatalizes the preceding consonant (handled separately)

CONSONANTS = {
    'б': 'ب',
    'п': 'ٻ',
    'т': 'ت',
    'ц': 'څ',
    'ж': 'ج',
    'ч': 'چ',
    'х': 'ح',
    'д': 'د',
    'р': 'ر',
    'з': 'ز',
    'с': 'س',
    'ш': 'ش',
    'щ': 'ص',   # щ = shch → ص (as shown in guide)
    'ع': 'ع',   # placeholder; ъ handled below
    'غ': 'غ',   # placeholder; г handled below
    'г': 'غ',
    'ф': 'ف',
    'к': 'ك',
    'л': 'ل',
    'м': 'م',
    'н': 'ن',
    'в': 'و',
    'й': 'ي',
}

# Hard sign ъ → ع (separator, shown as '' in guide — maps to ع in the chart)
# Soft sign ь → ا (palatalization marker shown as ا in chart)

SPECIAL = {
    'ъ': 'ع',   # hard sign
    'ь': 'ا',   # soft sign / palatalization
}

# Vowels: (initial_form, medial_form)
# initial = used at word start or after another vowel
# medial  = used after a consonant (diacritic-style attachment)
VOWELS = {
    'а': ('اَ',  'َ'),     # a  [a]
    'и': ('اِ',  'ِ'),     # i  [i]
    'у': ('اُ',  'ُ'),     # u  [u]
    'я': ('اَّ', 'َّ'),    # ya [ja/ʲæ]
    'ю': ('اُّ', 'ُّ'),    # yu [ju/ʲʉ]
    'э': ('ئ',   'ئ'),     # e  [ɛ]
    'е': ('ئٍ',  'ئٍ'),    # ye [je/ʲe/e]
    'ё': ('ؤٍ',  'ؤٍ'),    # yo [jo/ʲɵ]
    'о': ('ؤ',   'ؤ'),     # o  [o]
    'ы': ('ىٓ',  'ىٓ'),    # y  [ɨ]
}

ALL_VOWELS     = set(VOWELS.keys())
ALL_CONSONANTS = set(CONSONANTS.keys()) | set(SPECIAL.keys())

# ── Core converter ────────────────────────────────────────────────────────────

def russian_to_arabic(text):
    """
    Convert a Russian Cyrillic string to Arabized script.
    Rules:
      - Consonants → their Arabic letter directly.
      - Vowels at word-start or after another vowel → initial (full letter) form.
      - Vowels after a consonant → medial (diacritic) form.
      - Ь (soft sign) → ا marker after its consonant.
      - Ъ (hard sign) → ع separator.
      - Non-Cyrillic characters (spaces, punctuation, numbers) pass through as-is.
    """
    result = []
    prev_was_consonant = False
    is_word_start = True

    for char in text.lower():
        if char in CONSONANTS:
            result.append(CONSONANTS[char])
            prev_was_consonant = True
            is_word_start = False

        elif char in SPECIAL:
            result.append(SPECIAL[char])
            prev_was_consonant = False
            is_word_start = False

        elif char in VOWELS:
            initial, medial = VOWELS[char]
            if is_word_start or not prev_was_consonant:
                result.append(initial)
            else:
                result.append(medial)
            prev_was_consonant = False
            is_word_start = False

        else:
            # Space, punctuation, digits — pass through and reset word state
            result.append(char)
            prev_was_consonant = False
            is_word_start = (char == ' ' or char in '.,!?;:—–-\n\t')

    return ''.join(result)

# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    examples = [
        ('Привет', 'Hello'),
        ('Москва', 'Moscow'),
        ('Россия', 'Russia'),
        ('Добрый день!', 'Good day!'),
        ('Спасибо', 'Thank you'),
        ('Как дела?', 'How are you?'),
        ('Щука', 'Pike (fish)'),
        ('Цирк', 'Circus'),
        ('Южный', 'Southern'),
        ('Объект', 'Object (with hard sign)'),
        ('Соловьёв', 'Solovyov (with soft sign + ё)'),
    ]

    print(f"{'Russian':<25} {'Arabic':<25} {'Meaning'}")
    print('─' * 65)
    for ru, meaning in examples:
        ar = russian_to_arabic(ru)
        print(f'{ru:<25} {ar:<25} {meaning}')