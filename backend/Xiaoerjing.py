from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from xpinyin import Pinyin
import re
from punctuation_helper import preserve_and_process

# Mapping for Pinyin to Arabic words
pinyin_to_arabic = {
    "a": "اَ‎", "ai": "اَیْ‎", "an": "اً‎", "ang": "اَنْ‎",
    "ao": "اَوْ‎",
    "ba": "بَا‎", "bai": "بَیْ‎", "ban": "بًا‎", "bang": "بَانْ‎",
    "bao": "بَوْ‎", "bei": "بُوِ‎", "ben": "بٌ‎", "beng": "بِنْ‎",
    "bi": "بِ‎", "bian": "بِیًا‎", "biao": "بِیَوْ‎", "bie": "بِیَ‎",
    "bin": "بٍ‎", "bing": "بِیٍٔ‎", "bo": "بُوَ‎", "bu": "بُ‎",
    "ca": "ڞَا‎", "cai": "ڞَیْ‎", "can": "ڞًا‎", "cang": "ڞَانْ‎",
    "cao": "ڞَوْ‎", "ce": "ڞَ‎", "cen": "ڞٍ‎", "ceng": "ڞْ‌ٍ‎",
    "ci": "ڞِ‎", "cong": "ڞْو‎", "cou": "ڞِوْ‎", "cu": "ڞُ‎",
    "cuan": "ڞُوًا‎", "cui": "ڞُوِ‎", "cun": "ڞٌ‎", "cuo": "ڞُوَ‎",
    "cha": "چَا‎", "chai": "چَیْ‎", "chan": "چًا‎", "chang": "چَانْ‎",
    "chao": "چَوْ‎", "che": "چَ‎", "chen": "چٍ‎", "cheng": "چِنْ‎",
    "chi": "چِ‎", "chong": "چْو‎", "chou": "چِوْ‎", "chu": "چُ‎",
    "chuai": "چُوَیْ‎", "chuan": "چُوًا‎", "chuang": "چُوَانْ‎", "chui": "چُوِ‎",
    "chun": "چٌ‎", "chuo": "چُوَ‎",
    "da": "دَا‎", "dai": "دَیْ‎", "dan": "دًا‎", "dang": "دَانْ‎",
    "dao": "دَوْ‎", "de": "دْ‎", "dei": "دِيْ‎", "deng": "دِنْ‎",
    "di": "دِ‎", "dia": "دِیَا‎", "dian": "دِیًا‎", "diao": "دِیَوْ‎",
    "die": "دِیَ‎", "ding": "دٍ‎", "diu": "دِیُوْ‎", "dong": "دْو‎",
    "dou": "دِوْ‎", "du": "دُو‎", "duan": "دُوًا‎", "dui": "دُوِ‎",
    "dun": "دٌ‎", "duo": "دُوَ‎",
    "e": "عَ‎", "er": "عَر‎",
    "fa": "فَا‎", "fan": "فًا‎", "fang": "فَانْ‎", "fei": "فِ‎",
    "fen": "فٌ‎", "feng": "فِنْ‎", "fo": "فُوَ‎", "fou": "فِوْ‎",
    "fu": "فُ‎",
    "ga": "قَا‎", "gai": "قَیْ‎", "gan": "قًا‎", "gang": "قَانْ‎",
    "gao": "قَوْ‎", "ge": "قْ‎", "gei": "قِ‎", "gen": "قٍ‎",
    "geng": "قِنْ‎", "gong": "قْو‎", "gou": "قِوْ‎", "gu": "قُ‎",     "gua": "قُوَا‎", "guai": "قُوَیْ‎", "guan": "قُوًا‎", "guang": "قُوَانْ‎",
    "gui": "قُوِ‎", "gun": "قٌ‎", "guo": "قُوَ‎",
    "ha": "خَا‎", "hai": "خَیْ‎", "han": "خًا‎", "hang": "خَانْ‎",
    "hao": "خَوْ‎", "he": "حَ‎", "hei": "حِ‎", "hen": "حٍ‎",
    "heng": "حِنْ‎", "hong": "خْو‎", "hou": "خِوْ‎", "hu": "خُ‎",
    "hua": "خُوَا‎", "huai": "خُوَیْ‎", "huan": "خُوًا‎", "huang": "خُوَانْ‎",
    "hui": "خُوِ‎", "hun": "خٌ‎", "huo": "خُوَ‎",
    "ji": "ݣِ‎", "jia": "ݣِیَا‎", "jian": "ݣِیًا‎", "jiang": "ݣِیَانْ‎",
    "jiao": "ݣِیَوْ‎", "jie": "ݣِیَ‎", "jin": "ݣٍ‎", "jing": "ݣِنْ‎",
    "jiong": "ݣِیٌ‎", "jiu": "ݣِیُوْ‎", "ju": "ݣِیُوِ‎", "juan": "ݣِیُوًا‎",
    "jue": "ݣِیُوَ‎", "jun": "ݣٌ‎",
    "ka": "کَا‎", "kai": "کَیْ‎", "kan": "کًا‎", "kang": "کَانْ‎",
    "kao": "کَوْ‎", "ke": "کْ‎", "ken": "کٍ‎", "keng": "کِنْ‎",
    "kong": "کْو‎", "kou": "کِوْ‎", "ku": "کُ‎", "kua": "کُوَا‎",
    "kuai": "کُوَیْ‎", "kuan": "کُوًا‎", "kuang": "کُوَانْ‎", "kui": "کُوِ‎",
    "kun": "کٌ‎", "kuo": "کُوَ‎",
    "la": "لَا‎", "lai": "لَیْ‎", "lan": "لاً‎", "lang": "لَانْ‎",
    "lao": "لَوْ‎", "le": "لَ‎", "lei": "لُوِ‎", "leng": "لِنْ‎",
    "li": "لِ‎", "lia": "لِیَا‎", "lian": "لِیًا‎", "liang": "لِیَانْ‎",
    "liao": "لِیَوْ‎", "lie": "لِیَ‎", "lin": "لٍ‎", "ling": "لِیٍٔ‎",
    "liu": "لِیُوْ‎", "long": "لْو‎", "lou": "لِوْ‎", "lu": "لُ‎",
    "lv": "لِیُوِ‎", "luan": "لُوًا‎", "lve": "لِیُوَ‎", "lun": "لٌ‎",
    "luo": "لُوَ‎",
    "ma": "مَا‎", "mai": "مَیْ‎", "man": "مًا‎", "mang": "مَانْ‎",
    "mao": "مَوْ‎", "me": "مَ‎", "mei": "مُوِ‎", "men": "مٌ‎",
    "meng": "مِنْ‎", "mi": "مِ‎", "mian": "مِیًا‎", "miao": "مِیَوْ‎",
    "mie": "مِیَ‎", "min": "مٍ‎", "ming": "مِیٍٔ‎", "miu": "مِیُوْ‎",
    "mo": "مُوَ‎", "mou": "مِوْ‎", "mu": "مُ‎",
    "na": "نَا‎", "nai": "نَیْ‎", "nan": "نًا‎", "nang": "نَانْ‎",
    "nao": "نَوْ‎", "ne": "نَ‎", "nei": "نُوِ‎", "nen": "نٌ‎",
    "neng": "نِنْ‎", "ni": "نِ‎", "nian": "نِیًا‎", "niang": "نِیَانْ‎",
    "niao": "نِیَوْ‎", "nie": "نِیَ‎", "nin": "نٍ‎", "ning": "نِیٍٔ‎",
    "niu": "نِیُوْ‎", "nong": "نْو‎", "nu": "نُ‎", "nv": "نِیُوِ‎",
    "nuan": "نُوًا‎", "nve": "نِیُوَ‎", "nuo": "نُوَ‎",
    "o": "عِو‎", "ou": "عِوْ‎",
    "pa": "پَا‎", "pai": "پَیْ‎", "pan": "پًا‎", "pang": "پَانْ‎",
    "pao": "پَوْ‎", "pei": "پُوِ‎", "pen": "پٌ‎", "peng": "پِنْ‎",
    "pi": "پِ‎", "pian": "پِیًا‎", "piao": "پِیَوْ‎", "pie": "پِیَ‎",
    "pin": "پٍ‎", "ping": "پِیٍٔ‎", "po": "پُوَ‎", "pou": "پِوْ‎",
    "pu": "پُ‎",
    "qi": "ٿِ‎", "qia": "ٿِیَا‎", "qian": "ٿِیًا‎", "qiang": "ٿِیَانْ‎",
    "qiao": "ٿِیَوْ‎", "qie": "ٿِیَ‎", "qin": "ٿٍ‎", "qing": "ٿِنْ‎",
    "qiong": "ٿِیٌ‎", "qiu": "ٿِیُوْ‎", "qu": "ٿِیُوِ‎", "quan": "ٿِیُوًا‎",
    "que": "ٿِیُوَ‎", "qun": "ٿٌ‎",
    "ran": "ژًا‎", "rang": "ژَانْ‎", "rao": "ژَوْ‎", "re": "ژَ‎",
    "ren": "ژٍ‎", "reng": "ژِنْ‎", "ri": "ژِ‎", "rong": "ژٌ‎",
    "rou": "ژِوْ‎", "ru": "ژُو‎", "ruan": "ژُوًا‎", "rui": "ژُوِ‎",
    "run": "ژٌ‎", "ruo": "ژُوَ‎",
    "sa": "سَا‎", "sai": "سَیْ‎", "san": "سًا‎", "sang": "سَانْ‎",
    "sao": "سَوْ‎", "se": "سَ‎", "sen": "سٍ‎", "seng": "سِنْ‎",
    "si": "سِ‎", "song": "سٌ‎", "sou": "سِوْ‎", "su": "سُ‎",
    "suan": "صُوًا‎", "sui": "صُوِ‎", "sun": "صٌ‎", "suo": "صُوَ‎",
    "sha": "شَا‎", "shai": "شَیْ‎", "shan": "شًا‎", "shang": "شَانْ‎",
    "shao": "شَوْ‎", "she": "شَ‎", "shei": "شُوِ‎", "shen": "شٍ‎",
    "sheng": "شِنْ‎", "shi": "شِ‎", "shou": "شِوْ‎", "shu": "شُ‎",     "shua": "شُوَا‎", "shuai": "شُوَیْ‎", "shuan": "شُوًا‎", "shuang": "شُوَانْ‎",
    "shui": "شُوِ‎", "shun": "شٌ‎", "shuo": "شُوَ‎",
    "ta": "تَا‎", "tai": "تَیْ‎", "tan": "تًا‎", "tang": "تَانْ‎",
    "tao": "تَوْ‎", "te": "تْ‎", "teng": "تِنْ‎",
    "ti": "تِ‎", "tian": "تِیًا‎", "tiao": "تِیَوْ‎", "tie": "تِیَ‎",
    "ting": "تٍ‎", "tong": "طْو‎", "tou": "تِوْ‎", "tu": "تُ‎",
    "tuan": "طُوًا‎", "tui": "طُوِ‎", "tun": "طٌ‎", "tuo": "طُوَ‎",
    "wa": "وَا‎", "wai": "وَیْ‎", "wan": "وًا‎", "wang": "وَانْ‎",
    "wei": "وِ‎", "wen": "وٌ‎", "weng": "وِنْ‎", "wo": "وَ‎",
    "wu": "وُ‎",
    "xi": "ثِ‎", "xia": "ثِیَا‎", "xian": "ثِیًا‎", "xiang": "ثِیَانْ‎",
    "xiao": "ثِیَوْ‎", "xie": "ثِیَ‎", "xin": "ثٍ‎", "xing": "ثِنْ‎",
    "xiong": "ثِیٌ‎", "xiu": "ثِیُوْ‎", "xu": "ثِیُوِ‎", "xuan": "ثِیُوًا‎",
    "xue": "ثِیُوَ‎", "xun": "ثٌ‎",
    "ya": "یَا‎", "yan": "یًا‎", "yang": "یَانْ‎", "yao": "یَوْ‎",
    "ye": "یَ‎", "yi": "ءِ‎", "yin": "ءٍ‎", "ying": "یٍ‎",
    "yong": "یٌ‎", "you": "یُوْ‎", "yu": "یُوِ‎", "yuan": "یُوًا‎",
    "yue": "یُوَ‎", "yun": "ءٌ‎",
    "za": "زَا‎", "zai": "زَیْ‎", "zan": "زًا‎", "zang": "زَانْ‎",
    "zao": "زَوْ‎", "ze": "زَ‎", "zei": "زِيْ‎", "zen": "زٍ‎",
    "zeng": "زِنْ‎", "zi": "زِ‎", "zong": "ظْو‎", "zou": "زِوْ‎",
    "zu": "زُو‎", "zuan": "زُوًا‎", "zui": "ظُوِ‎", "zun": "ظٌ‎",
    "zuo": "ظُوَ‎",
    "zha": "جَا‎", "zhai": "جَیْ‎", "zhan": "جًا‎", "zhang": "جَانْ‎",
    "zhao": "جَوْ‎", "zhe": "جَ‎", "zhei": "جُوِ‎", "zhen": "جٍ‎",
    "zheng": "جِنْ‎", "zhi": "جِ‎", "zhong": "جْو‎", "zhou": "جِوْ‎",
    "zhu": "جُ‎", "zhua": "جُوَا‎", "zhuai": "جُوَیْ‎", "zhuan": "جُوًا‎",
    "zhuang": "جُوَانْ‎", "zhui": "جُوِ‎", "zhun": "جٌ‎", "zhuo": "جُوَ‎", 
    ",":"،", "。":".", "、":"،", "，":"،", "！": "!", 
    "？": "؟", "；": "؛", "：“": "«", "：": ":", "”": "»", 
    "（": "(", "）": ")", "【": "[", "】": "]", "《": "«", 
    "》": "»", "——": "—", "～": "~", "·": "·", "。": ".", 
    "、": "،", "；": "؛", "「": "“", "」": "”", "〈": "‹", 
    "〉": "›", "「": "‹", "」": "›", "－": "–", "…": "…",
    "·": "·", "※": "*", "♪": "♪", "☆": "☆", "→": "→",
    "←": "←", "↑": "↑", "↓": "↓", "☀": "☀", "✈": "✈", 
    "☕": "☕", "★": "★", "♪": "♪", "☆": "☆", "✓": "✓", 
    "✖": "✖"
}

# Mapping for Western numerals to Indo-Arabic numerals
western_to_arabic = {'1': '١', '2': '٢', '3': '٣', '4': '۴', '5': '۵',
                     '6': '٦', '7': '٧', '8': '٨', '9': '٩', '0': '٠'}

def combine_pinyin_with_tones_word(chinese_word):
    """Process a single Chinese word (without punctuation)."""
    p = Pinyin()
    pinyin_list = p.get_pinyin(chinese_word, ' ').split()
    pinyin_with_tones_str = p.get_pinyin(chinese_word, tone_marks='numbers')
    tone_parts = pinyin_with_tones_str.split('-')
    
    arabic_words = []
    for word in pinyin_list:
        if word.isdigit():
            arabic_words.append(word)
        else:
            arabic_words.append(pinyin_to_arabic.get(word, ""))
    
    tone_numbers = []
    for word in tone_parts:
        tone_number = ''.join([western_to_arabic[char] if char in western_to_arabic else '' for char in word])
        tone_numbers.append(tone_number)
    
    min_length = min(len(arabic_words), len(tone_numbers))
    arabic_words = arabic_words[:min_length]
    tone_numbers = tone_numbers[:min_length]
    combined = [f"{word}{tone}" for word, tone in zip(arabic_words, tone_numbers)]
    return ''.join(combined)

def combine_pinyin_with_tones(chinese_text):
    """Process entire text while preserving punctuation."""
    return preserve_and_process(chinese_text, combine_pinyin_with_tones_word)

def clean_string(input_string):
    # Regular expression to match Indo-Arabic numerals from both sets
    pattern = r'(?<=[0-9])[٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹]+(?=[^٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹]|$)'
    # Replace the matched pattern with an empty string
    cleaned_string = re.sub(pattern, '', input_string)
    return cleaned_string

# Bot handlers
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Send me Chinese text, and I'll transliterate it to Xiao'erjing.")

async def convert(update: Update, context: CallbackContext):
    chinese_text = update.message.text
    arabic_equivalent = combine_pinyin_with_tones(chinese_text)
    arabic_equivalent = clean_string(arabic_equivalent)
    await update.message.reply_text(arabic_equivalent)

async def main():
    # Replace 'YOUR_TOKEN' with your bot's API token
    application = Application.builder().token("7601039743:AAHE-JlQFUEocRtmDy3K9S_Bcl2Zp1mgdGE").build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start))

    # Handle messages with the Spanish to Aljamiado conversion
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert))

    # Start the bot
    await application.run_polling()

if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()  # This allows asyncio to run in an already running event loop (important for environments like Jupyter)

    # Run the main function
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())