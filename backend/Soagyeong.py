from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from hangul_jamo import decompose_syllable
import re

# Korean to Arabic transliteration function
def korean_to_arabic(text):
    # Mapping of Korean jamo to Arabic equivalents
    transliteration_map = {
        # Consonants
        "ㄱ": "گ", "ㄲ": "گّ", "ㄴ": "ن", "ㄷ": "د", "ㄸ": "دّ",
        "ㄹ": "ل", "ㅁ": "م", "ㅂ": "ب", "ㅃ": "بّ", "ㅅ": "س",
        "ㅆ": "سّ", "ㅇ": "ڭ", "ㅈ": "ج", "ㅉ": "جّ", "ㅊ": "چ", "ㅋ": "ك",
        "ㅌ": "ت", "ㅍ": "پ", "ㅎ": "ھ", "ㆁ": "ڭ", "ㅿ": "ز", "ㆆ":"ء", 
        "ㆅ":"ھّ", "ㆄ":"ف", "ㆃ":"ڭز", "ㆂ":"ڭس", "ㆀ":"غ", "ㅱ":"ح", "ㅸ":"ڤ",
        # Vowels
        "ㅏ": "ە", "ㅐ": "ؽ", "ㅑ": "عە", "ㅒ": "عؽ",
        "ㅓ": "ة", "ㅔ": "ێ", "ㅕ": "عة", "ㅖ": "عێ",
        "ㅗ": "ۆ", "ㅘ": "ۆە", "ㅙ": "ۆؽ", "ㅚ": "ۆي",
        "ㅛ": "عۆ", "ㅜ": "و", "ㅝ": "وة", "ㅞ": "وێ", "ㅟ": "وي",
        "ㅠ": "عو", "ㅢ": "ىي", "ㅡ": "ى", "ㅣ": "ي", "ㆍ": "ۀ", "ㆎ": "ۀي", "ᆢ":"عۀ",

        # Special cases
        "ㄳ": "گس","ㄵ": "نج","ㄶ": "نھ","ㄳ": "گس","ㄺ": "لگ","ㄻ": "لم","ㄼ": "لب", "ㄽ": "لس", "ㅄ": "بس", "ㄿ": "لپ", "ㄾ": "لت", "ㅀ": "لھ"
    }

    arabic_text = ""
    prev_syllable = None  # To track the previous Hangul syllable block

    for char in text:
        try:
            if '\uAC00' <= char <= '\uD7A3':  # Hangul syllable block
                decomposed = decompose_syllable(char)  # Decompose into jamo
                initial, medial, final = decomposed[0], decomposed[1], decomposed[2] if len(decomposed) == 3 else None

                # Handle the initial consonant (ㅇ at the beginning)
                if initial == "ㅇ":  # Special handling for ㅇ at the start
                    if prev_syllable is None:  # No preceding syllable
                        arabic_text += "ا"  # 'ㅇ' becomes 'ا' at the start of the syllable
                    else:  # Check the previous syllable and decide if it should be 'ء' or omitted
                        if transliteration_map.get(prev_syllable[-1], "").strip() in ["ە", "ۀ", "عۀ", "ۀي", "ؽ", "ة", "ێ", "عا", "عێ", "ۆ", "و", "وي", "عو", "ىي", "ى", "ي"]:
                            arabic_text += "ء"  # If previous syllable ends with a vowel, use 'ء'
                        else:
                            arabic_text += "ا"  # Otherwise, treat as 'ا'
                else:
                    arabic_text += transliteration_map.get(initial, "")

                # Handle the medial vowel (add directly)
                arabic_text += transliteration_map.get(medial, "")

                # Handle the final consonant
                if final == "ㅇ":  # ㅇ at the end of the syllable
                    arabic_text += "ڭ"
                elif final:
                    arabic_text += transliteration_map.get(final, "")

                prev_syllable = decomposed  # Update the previous syllable
            elif char in transliteration_map:  # Handle standalone jamo
                arabic_text += transliteration_map[char]
            else:
                arabic_text += char  # Preserve non-Hangul characters
        except ValueError:
            arabic_text += char  # Add unsupported characters as-is

    return arabic_text


def adjust_arabic_output(arabic_text):
    consonants = "زغچبحبّپسسّججّددّتگگّكمنلھڭ"
    vowels = "يىەةۀوۆعؽێ"
    adjusted_text = ""
    
    for i, char in enumerate(arabic_text):
        if char == "ا":
            if i == 0 or arabic_text[i - 1] == " ":  # If at the start or preceded by a space
                adjusted_text += char
            elif arabic_text[i - 1] in consonants:  # If preceded by a consonant
                continue  # Omit "ا"
            elif arabic_text[i - 1] in vowels:  # If preceded by a vowel
                adjusted_text += "ء"
            else:
                adjusted_text += char  # Default case, keep "ا"
        else:
            adjusted_text += char  # Keep other characters unchanged
    
    adjusted_text = re.sub(r'ءع', 'ع', adjusted_text)
    adjusted_text = re.sub(r'(?<!\w)اع', 'ع', adjusted_text)
    adjusted_text = re.sub(r'ع', 'ي', adjusted_text)
    adjusted_text = re.sub(r'ة', 'ا', adjusted_text)
    adjusted_text = re.sub(r'ۆءێ', 'ۆئێ', adjusted_text)
    adjusted_text = re.sub(r'ؽءا', 'ؽئا', adjusted_text)
    adjusted_text = re.sub(r'يءؽ', 'يئؽ', adjusted_text)
    adjusted_text = re.sub(r'ێءي', 'ێئي', adjusted_text)
    adjusted_text = re.sub(r'ەءە', 'ەءە', adjusted_text)
    adjusted_text = re.sub(r'وءە', 'وؤە', adjusted_text)
    adjusted_text = re.sub(r'ؽءێ', 'ؽئێ', adjusted_text)
    adjusted_text = re.sub(r'ەءؽ', 'ەئؽ', adjusted_text)
    adjusted_text = re.sub(r'ەءۆ', 'ەؤۆ', adjusted_text)
    adjusted_text = re.sub(r'ؽءو', 'ؽئو', adjusted_text)
    adjusted_text = re.sub(r'ۆءە', 'ۆؤە', adjusted_text)
    adjusted_text = re.sub(r'ێءۆ', 'ێئۆ', adjusted_text)
    adjusted_text = re.sub(r'وءۆ', 'وؤۆ', adjusted_text)
    adjusted_text = re.sub(r'ەءا', 'ەآ', adjusted_text)
    adjusted_text = re.sub(r'اءي', 'ائي', adjusted_text)
    adjusted_text = re.sub(r'اءە', 'اءە', adjusted_text)
    adjusted_text = re.sub(r'اءۆ', 'اؤۆ', adjusted_text)
    adjusted_text = re.sub(r'ؽءي', 'ؽئي', adjusted_text)
    adjusted_text = re.sub(r'ەءو', 'ەؤو', adjusted_text)
    adjusted_text = re.sub(r'ێءە', 'ێئە', adjusted_text)
    adjusted_text = re.sub(r'ەءێ', 'ەئێ', adjusted_text)
    adjusted_text = re.sub(r'يءي', 'يئي', adjusted_text)
    adjusted_text = re.sub(r'وءؽ', 'وئؽ', adjusted_text)
    adjusted_text = re.sub(r'يءێ', 'يئێ', adjusted_text)
    adjusted_text = re.sub(r'يءە', 'يئە', adjusted_text)
    adjusted_text = re.sub(r'ؽءە', 'ؽئە', adjusted_text)
    adjusted_text = re.sub(r'ؽءۆ', 'ؽئۆ', adjusted_text)
    adjusted_text = re.sub(r'وءا', 'وؤا', adjusted_text)
    adjusted_text = re.sub(r'ێءا', 'ێئا', adjusted_text)
    adjusted_text = re.sub(r'ێءؽ', 'ێئؽ', adjusted_text)
    adjusted_text = re.sub(r'يءو', 'يئو', adjusted_text)
    adjusted_text = re.sub(r'وءێ', 'وئێ', adjusted_text)
    adjusted_text = re.sub(r'ێءێ', 'ێئێ', adjusted_text)
    adjusted_text = re.sub(r'ؽءؽ', 'ؽئؽ', adjusted_text)
    adjusted_text = re.sub(r'اءو', 'اؤو', adjusted_text)
    adjusted_text = re.sub(r'اءؽ', 'ائؽ', adjusted_text)
    adjusted_text = re.sub(r'اءێ', 'ائێ', adjusted_text)
    adjusted_text = re.sub(r'ۆءا', 'ۆؤا', adjusted_text)
    adjusted_text = re.sub(r'وءي', 'وئي', adjusted_text)
    adjusted_text = re.sub(r'يءا', 'يئا', adjusted_text)
    adjusted_text = re.sub(r'ێءو', 'ێئو', adjusted_text)
    adjusted_text = re.sub(r'وءو', 'وؤو', adjusted_text)
    adjusted_text = re.sub(r'ۆءو', 'ۆؤو', adjusted_text)
    adjusted_text = re.sub(r'يءۆ', 'يئۆ', adjusted_text)
    adjusted_text = re.sub(r'ۆءۆ', 'ۆؤۆ', adjusted_text)
    adjusted_text = re.sub(r'ەءي', 'ەئي', adjusted_text)
    adjusted_text = re.sub(r'اءا', 'اآ', adjusted_text)
    adjusted_text = re.sub(r'ۆءي', 'ۆئي', adjusted_text)
    adjusted_text = re.sub(r'ۆءؽ', 'ۆئؽ', adjusted_text)
    adjusted_text = re.sub(r'يءى', 'يئى', adjusted_text)
    adjusted_text = re.sub(r'اءى', 'ائى', adjusted_text)
    adjusted_text = re.sub(r'ەءى', 'ەئى', adjusted_text)
    adjusted_text = re.sub(r'ؽءى', 'ؽئى', adjusted_text)
    adjusted_text = re.sub(r'ۆءى', 'ۆئى', adjusted_text)
    adjusted_text = re.sub(r'ێءى', 'ێئى', adjusted_text)
    adjusted_text = re.sub(r'وءى', 'وئى', adjusted_text)
    adjusted_text = re.sub(r'ىءا', 'ىئا', adjusted_text)
    adjusted_text = re.sub(r'ىءە', 'ىئە', adjusted_text)
    adjusted_text = re.sub(r'ىءو', 'ىئو', adjusted_text)
    adjusted_text = re.sub(r'ىءؽ', 'ىئؽ', adjusted_text)
    adjusted_text = re.sub(r'ىءێ', 'ىئێ', adjusted_text)
    adjusted_text = re.sub(r'ىءي', 'ىئي', adjusted_text)
    adjusted_text = re.sub(r'ىءۆ', 'ىئۆ', adjusted_text)
    adjusted_text = re.sub(r'ىءى', 'ىئى', adjusted_text)
    adjusted_text = re.sub(r'اا', 'آ', adjusted_text)
    adjusted_text = re.sub(r'اە', 'ا', adjusted_text)
    adjusted_text = re.sub(r'ح', 'و', adjusted_text)
    #adjusted_text = re.sub(r"(?<!زغچبحبّپسسّججّددّتگگّكمنئءؤآلھڭيىەةۀوۆعؽێ)ا(?!زغچبحبّپسسّججّددّتگگّكمنلھڭئءؤآيىەةۀوۆعؽێ)", "اە", adjusted_text)
    #adjusted_text = re.sub(r"(?<!زغچبحبّپسسّججّددّتگگّكمنلھڭيءئؤآىەةۀوۆعؽێ)آ(?!زغچبحبّپسسّججّددّتگگّكمنلھئءؤآڭيىەةۀوۆعؽێ)", "آە", adjusted_text)




    return adjusted_text