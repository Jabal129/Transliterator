import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Define the Spanish to Aljamiado mapping
def convert_to_aljamiado(spanish_text):
    # Define mappings for vowel sequences
    vowel_sequences_beginning = {
    'Aa': 'اَاَ', 'Ae': 'اَءَا', 'Ai': 'اَيِ', 'Ao': 'اَوُ', 'Au': 'اَوُ',
    'Ea': 'ءَااَ', 'Ee': 'ءَاءَا', 'Ei': 'ءَايِ', 'Eo': 'ءَاوُ', 'Eu': 'ءَاوُ',
    'Ia': 'اِيَ', 'Ie': 'اِيَا', 'Ii': 'اِيِ', 'Io': 'اِيُ', 'Iu': 'اِيُ',
    'Oa': 'اُوَ', 'Oe': 'اُوَا', 'Oi': 'اُيِ', 'Oo': 'اُوُ', 'Ou': 'اُوُ',
    'Ua': 'اُوَ', 'Ue': 'اُوَا', 'Ui': 'اُيِ', 'Uo': 'اُوُ', 'Uu': 'اُوُ'
    }

    vowel_sequences_middle_final = {
    'Aa': 'َاَ', 'Ae': 'َءَا', 'Ai': 'َيِ', 'Ao': 'َوُ', 'Au': 'َوُ', 'Ay': 'َي',
    'Ea': 'َااَ', 'Ee': 'َاءَا', 'Ei': 'َايِ', 'Eo': 'َاوُ', 'Eu': 'َاوُ', 'Ey': 'َاي',
    'Ia': 'ِيَ', 'Ie': 'ِيَا', 'Ii': 'ِيِ', 'Io': 'ِيُ', 'Iu': 'ِيُ', 'Iy': 'ِي',
    'Oa': 'ُوَ', 'Oe': 'ُوَا', 'Oi': 'ُيِ', 'Oo': 'ُوُ', 'Ou': 'ُوُ', 'Oy': 'ُي',
    'Ua': 'ُوَ', 'Ue': 'ُوَا', 'Ui': 'ُيِ', 'Uo': 'ُوُ', 'Uu': 'ُوُ', 'Uy': 'ُي'
    }



    # Define mappings for digraphs and single characters
    digraphs = {
    'ch': 'جّ', 'rr': 'رّ', 'll': 'لّ', 'ss': 'شّ',
    'bb': 'بّ', 'dd': 'دّ', 'ff': 'فّ', 'gg': 'غّ',
    'hh': 'هّ', 'mm': 'مّ', 'nn': 'نّ', 'pp': 'بّ', 'tt': 'تّ', 
    'vv': 'وّ', 'zz': 'زّ'
    }

    spanish_to_aljamiado = {
        'b': 'ب', 'p': 'بّ', 'v': 'ب',
        'c': 'ك', 'ç': 'س', 'm': 'م',
        'd': 'ذ', 'z': 'س', 'h': 'ه',
        'g': 'غ', 'j': 'ج', ',': '،',
        'x': 'كْش', 's': 'ش', 'w': 'و',
        't': 'ت', 'k': 'ك', 
        'r': 'ر', 'l': 'ل', 'f': 'ڢ',
        'n': 'ن', 'ñ': 'نّ', 'q': 'ك',
        'a': 'َ', 'á': 'َ', 'e': 'َا', 'é': 'َا',
        'i': 'ِ', 'í': 'ِ', 'o': 'ُ', 'ó': 'ُ',
        'u': 'ُ', 'ú': 'ُ'
    }

    vowels_initial = {
        'a': 'اَ', 'á': 'اَ',
        'e': 'ءَا', 'é': 'ءَا',
        'i': 'اِ', 'í': 'اِ',
        'o': 'اُ', 'ó': 'اُ',
        'u': 'اُ', 'ú': 'اُ'
    }

    # Function to process a single word
    def process_word(word):
        # Replace accented vowels with their non-accented versions
        word = word.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

        # Replace 'qu' with a special marker for 'q'
        word = re.sub(r'[qQ]u', 'ک', word)  # Replace 'qu' directly with Persian-style Kaf
        word = re.sub(r'[qQ]ü', 'کْو', word)
        word = re.sub(r'[cC]h', 'جّ', word)

        # Replace 'q' with Persian-style Kaf
        word = word.replace('q', 'ک').replace('Q', 'ک')
        word = word.replace('k', 'ک').replace('K', 'ک')

        # Replace 'gu' with a special marker for 'g'
        word = re.sub(r'[gG]ui', 'قِ', word)  # Replace 'gu' directly with Qaf
        word = re.sub(r'[gG]ue', 'قَا', word)
        word = re.sub(r'[gG]ua', 'قْوَ', word)
        word = re.sub(r'[gG]üe', 'قْوَا', word)
        word = re.sub(r'[gG]üi', 'قْوِ', word)
        # word = re.sub(r'[hH]u', 'و', word)

        # if word.startswith('[hH]'):
        #     word = 'ا' + word[1:]  # Replace initial 'h' with Alif

            # Check for vowel sequences in the beginning of the word
        for seq, aljamiado_seq in vowel_sequences_beginning.items():
            if word.lower().startswith(seq.lower()):
                word = re.sub(f'^{seq}', aljamiado_seq, word, flags=re.IGNORECASE)
                break
        # Handle vowels at the beginning of the word
        
        if word and word[0].lower() in vowels_initial:
            initial_vowel = vowels_initial[word[0].lower()]
            word = initial_vowel + word[1:]
        
        # Check for vowel sequences in the middle or at the end of the word
        for seq, aljamiado_seq in vowel_sequences_middle_final.items():
            word = re.sub(seq, aljamiado_seq, word, flags=re.IGNORECASE)

        # Handle digraphs
        for digraph, aljamiado_char in digraphs.items():
            word = word.replace(digraph, aljamiado_char)

        # Convert the rest of the word character by character
        converted_word = ''
        for i, char in enumerate(word):
            # Special rule for 'd'
            if char.lower() == 'd':
                if i == 0 or (i > 0 and word[i - 1].lower() in ['m', 'n']):
                    converted_word += 'د'  # 'د'
                else:
                    converted_word += 'ذ'  # 'ذ'
            elif char.lower() == 'y':
                # Special rule for 'y'
                if i == len(word) - 1 or word[i + 1] == ' ':
                    converted_word += 'اِ'  # 'اِ' when 'y' is followed by space or it's the last character
                else:
                    converted_word += 'ي'  # Default 'y' behavior
            else:
                converted_word += spanish_to_aljamiado.get(char.lower(), char)
        
        arabic_consonants = "بتثجحخدذرزسشصضطظعغفقكلمنهوي"  # Arabic consonants excluding Alif
        converted_word = re.sub(rf"([{arabic_consonants}])(?![ًٌٍَُِْ])", r"\1ْ", converted_word)

        # Post-process the converted word to apply kasra and fatha rules
        converted_word = re.sub(r'كِ', 'سِ', converted_word)  # If ك is followed by kasra, convert to س
        converted_word = re.sub(r'كَا', 'سَا', converted_word)  # If ك is followed by fatha and alif, convert to س
        converted_word = re.sub(r'غِ', 'جِ', converted_word)  # If غ is followed by kasra, convert to ج
        converted_word = re.sub(r'غَا', 'جَا', converted_word)  # If غ is followed by fatha and alif, convert to ج
        converted_word = re.sub(r'ک', 'ك', converted_word)  # If غ is followed by fatha and alif, convert to ج
        converted_word = re.sub(r'ق', 'غ', converted_word)  # If غ is followed by fatha and alif, convert to ج
        # converted_word = re.sub(r'هَا', 'ءَا', converted_word)  # If غ is followed by fatha and alif, convert to ج
        # converted_word = re.sub(r'ه', 'ا', converted_word)  # If غ is followed by fatha and alif, convert to ج
        converted_word = re.sub(r'ّْ', 'ّ', converted_word)  # If غ is followed by fatha and alif, convert to ج
        converted_word = re.sub(r'َِ', 'ِيَ', converted_word)  # If غ is followed by fatha and alif, convert to ج
        converted_word = re.sub(r'مْب', 'نْب', converted_word)  # If غ is followed by fatha and alif, convert to ج


        return converted_word


    # Process the input text word by word
    words = spanish_text.split()
    aljamiado_text = ' '.join(process_word(word) for word in words)

    return aljamiado_text