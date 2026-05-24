import re
from dataclasses import dataclass
from typing import List, Pattern


@dataclass
class Rule:
    pattern: Pattern
    replacement: str


class PortugueseToSpanishTransliterator:
    """
    Portuguese → Spanish-style orthographic transliterator.

    This is NOT a translator.
    It mechanically Hispanicizes Portuguese spelling.
    """

    def __init__(self, aggressive: bool = False):
        self.rules: List[Rule] = [
            #
            # Stage 1 — Morphological endings
            #
            Rule(re.compile(r'ções\b', re.IGNORECASE), 'zoes'),
            Rule(re.compile(r'ção\b', re.IGNORECASE), 'zao'),
            Rule(re.compile(r'sões\b', re.IGNORECASE), 'soes'),
            Rule(re.compile(r'são\b', re.IGNORECASE), 'sao'),
            

            #
            # Stage 2 — Nasal vowels
            #
            Rule(re.compile(r'ões\b', re.IGNORECASE), 'oes'),
            Rule(re.compile(r'ão\b', re.IGNORECASE), 'ao'),
            Rule(re.compile(r'ãe', re.IGNORECASE), 'ae'),
            Rule(re.compile(r'õe', re.IGNORECASE), 'oe'),
            Rule(re.compile(r'uai', re.IGNORECASE), 'uay'),

            Rule(re.compile(r'am\b', re.IGNORECASE), 'an'),
            Rule(re.compile(r'em\b', re.IGNORECASE), 'en'),

            #
            # Stage 3 — Palatals
            #
            Rule(re.compile(r'nh', re.IGNORECASE), 'ñ'),
            Rule(re.compile(r'lh', re.IGNORECASE), 'll'),
            Rule(re.compile(r'v', re.IGNORECASE), 'vv'), # to be post-processed into 'v' or 'b' depending on context

            #
            # Stage 4 — Cedilla
            #
            Rule(re.compile(r'ç(?=[eiéí])', re.IGNORECASE), 'z'),
            Rule(re.compile(r'ç', re.IGNORECASE), 'c'),

            #
            # Stage 5 — Accent normalization
            #
            Rule(re.compile(r'â'), 'á'),
            Rule(re.compile(r'ê'), 'e'),
            Rule(re.compile(r'ô'), 'o'),
            Rule(re.compile(r'à'), 'a'),
            Rule(re.compile(r'ã'), 'a'),
            Rule(re.compile(r'õ'), 'o'),

            Rule(re.compile(r'Â'), 'Á'),
            Rule(re.compile(r'Ê'), 'E'),
            Rule(re.compile(r'Ô'), 'O'),
            Rule(re.compile(r'À'), 'A'),
            Rule(re.compile(r'Ã'), 'A'),
            Rule(re.compile(r'Õ'), 'O'),
            Rule(re.compile(r'ou', re.IGNORECASE), 'ow'),
            Rule(re.compile(r'ph', re.IGNORECASE), 'f'),
            Rule(re.compile(r'th', re.IGNORECASE), 't'),
        ]


    def transliterate(self, text: str) -> str:
        """
        Apply all transliteration rules in order.
        """

        for rule in self.rules:
            text = rule.pattern.sub(rule.replacement, text)

        return text


if __name__ == "__main__":

    engine = PortugueseToSpanishTransliterator()

    samples = [
        "O irmão chegou amanhã.",
        "Informações sobre a nação.",
        "Os leões cantam.",
        "Português moderno.",
        "O vinho da manhã.",
        "As televisões são novas.",
    ]

    for s in samples:
        print(f"PT : {s}")
        print(f"ES : {engine.transliterate(s)}")
        print()