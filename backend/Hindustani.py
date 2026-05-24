from aksharamukha import transliterate

def hindi_to_arabic(text):
    urduscript = transliterate.process(
        "Devanagari",
        "Urdu",
        text    )
    return urduscript