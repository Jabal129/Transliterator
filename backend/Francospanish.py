"""
hispanicize_french.py
=====================
Converts French orthography to a Hispanicized (Spanish-orthography) form,
following the systematic transliteration rules developed in the companion guide.

Rules applied (in order of priority):
  1. Nasal vowel digraphs (context-sensitive)
  2. Vowel digraphs (eau, au, ai, ei, oi, ou, eu, œu …)
  3. Consonant clusters (ch, gn, qu, ph, ss, ll …)
  4. Individual phoneme mappings
  5. Word-final silent consonant deletion
  6. Double-consonant simplification
  7. Silent ‹h› deletion
  8. Stress accent adjustment

Usage:
    python hispanicize_french.py                     # interactive prompt
    python hispanicize_french.py "bonjour"           # single word
    python hispanicize_french.py -f input.txt        # file (one word/line)
"""

import re
import sys
import unicodedata
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm(text: str) -> str:
    """Lowercase and NFC-normalize."""
    return unicodedata.normalize("NFC", text.lower())


def _has_accent(ch: str) -> bool:
    return unicodedata.combining(unicodedata.normalize("NFD", ch)[1]) if len(
        unicodedata.normalize("NFD", ch)) > 1 else False


# ---------------------------------------------------------------------------
# Core transliteration engine
# ---------------------------------------------------------------------------

class FrenchHispanicizer:
    """
    Applies ordered rewrite rules to convert French spelling to a
    Hispanicized form.  Rules are expressed as (pattern, replacement) pairs
    and are applied left-to-right, longest-match first within each pass.

    Pass order matters:
      Pass 1  — multi-char nasal clusters (must precede vowel digraphs)
      Pass 2  — vowel digraphs
      Pass 3  — consonant clusters and digraphs
      Pass 4  — single-character phoneme mappings
      Pass 5  — word-final silent letter deletion
      Pass 6  — double-consonant simplification
      Pass 7  — residual cleanup
    """

    # ------------------------------------------------------------------
    # Pass 1: Nasal vowel sequences
    # Order matters: longest/most-specific patterns first.
    # Strategy: French nasal vowel + (silent) nasal consonant →
    #   de-nasalize to a plain vowel + explicit nasal consonant.
    # ------------------------------------------------------------------
    NASAL_RULES: list[tuple[str, str]] = [
        # /ɑ̃/  (an, am, en, em before consonant or end)
        (r"an(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "an"),
        (r"am(?=[bp])", "am"),          # am before labial stays am
        (r"am(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "an"),
        (r"en(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "an"),
        (r"em(?=[bp])", "am"),
        (r"em(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "an"),
        # /ɛ̃/  (in, im, ain, aim, ein, yn, ym)
        (r"ain(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "en"),
        (r"aim(?=[bp])", "em"),
        (r"aim(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "en"),
        (r"ein(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "en"),
        (r"in(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "en"),
        (r"in$", "in"),                 # word-final /ɛ̃/ → in
        (r"im(?=[bp])", "im"),
        (r"im(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "en"),
        (r"yn(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "en"),
        (r"ym(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "en"),
        # /ɔ̃/  (on, om)
        (r"on(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "on"),
        (r"om(?=[bp])", "om"),
        (r"om(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "on"),
        # /œ̃/  (un, um)
        (r"un(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "un"),
        (r"um(?=[bp])", "um"),
        (r"um(?=[^aeiouâàäéèêëîïôùûüœæhy]|$)", "un"),
    ]

    # ------------------------------------------------------------------
    # Pass 2: Vowel digraphs and accented vowels
    # ------------------------------------------------------------------
    VOWEL_RULES: list[tuple[str, str]] = [
        # eau / au → o
        (r"eaux?", "o"),
        (r"aux?", "o"),          # 'aux' plural → 'o' (silent x)
        # -ieux, -ieu → yo  (/jø/ → yo)
        (r"ieux", "yo"),
        (r"ieu", "yo"),
        # -euil, -ueil → oy  (/œj/ → oy)
        (r"euil", "oll"),
        (r"ueil", "oll"),
        # -eil → ey  (/ɛj/ → ey)
        (r"eil", "ell"),
        # -uil → oy  (/ɥj/)
        (r"uil", "oll"),
        # ai / ei → e
        (r"ai", "e"),
        (r"ei", "e"),
        # oi → ua  (/wa/ diphthong)
        (r"oi", "ua"),
        # ou → u
        (r"oui", "ui"),         # 'oui' /wi/ → ui
        (r"ou", "u"),
        # eu / œu — distinguish open vs closed syllable
        (r"œu", "e"),           # bœuf → bef (always /œ/)
        (r"eu(?=[rlvfzj])", "e"),   # peur, fleur, veuve → e
        (r"eu", "o"),           # feu, bleu, jeu → o
        # œ ligature alone
        (r"œ", "e"),
        # æ ligature (rare)
        (r"æ", "e"),
        # Accented vowels → plain equivalents
        (r"[âàä]", "a"),
        (r"[êèë]", "e"),
        (r"é", "e"),
        (r"[îï]", "i"),
        (r"[ôö]", "o"),
        (r"[ûùü]", "u"),
    ]
    # Pass 4: Remaining single-character rules
    # ------------------------------------------------------------------
    SINGLE_CHAR_RULES: list[tuple[str, str]] = [
        # z → s  (French /z/)
        (r"z", "z"),
        # y (vowel, between consonants) stays y
        # k stays k
        # No further single-char rules needed for remaining consonants
    ]

    # ------------------------------------------------------------------
    # Pass 3: Consonant clusters and digraphs
    # ------------------------------------------------------------------
    CONSONANT_CLUSTER_RULES: list[tuple[str, str]] = [
        # ph → f
        (r"ph", "f"),
        # ch → ch  (French /ʃ/ → Spanish ch /tʃ/, stays the same grapheme)
        # Protect 'ch' from the later h-deletion pass by temporarily encoding it.
        (r"ch", "\x01CH\x01"),
        # gn → ñ  (/ɲ/)
        (r"gn", "ñ"),
        # qu before front vowels: keep qu (Spanish convention)
        (r"qu(?=[aouâàôùû])", "cu"),
        # qu before back vowels/consonants: cu
        (r"qu(?=[ei])", "qu"),
        # gu before e/i (French /g/, silent u): drop u → g
        (r"gu(?=[ei])", "g"),
        # ge, gi → ye, yi  (/ʒ/ → y)
        (r"ge(?=[aouâàôùû])", "je"),  # ge before back vowel (liaison)
        (r"ge", "je"),
        (r"gi", "ji"),
        # j → y  (/ʒ/)
        (r"j", "j"),
        # c before e/i → s  (/s/)
        (r"c(?=[eiéèêëîï])", "c"),
        # ç → s
        (r"ç", "z"),
        # ss → s  (intervocalic)
        (r"ss", "s"),
        # x between vowels → gs  (/gz/, e.g. examen)
        (r"(?<=[aeiouâàäéèêëîïôùûü])x(?=[aeiouâàäéèêëîïôùûü])", "gs"),
        # x elsewhere → cs  (/ks/)
        (r"x", "cs"),
        # -tion → -cion  (/sjɔ̃/ → -cion, matching Spanish convention)
        (r"tion", "cion"),
        # v → b  (Spanish lacks /v/)
        # NOTE: we use 'b' as default; keep as 'v' where Spanish cognate uses v.
        # For a transliteration system, 'b' is the phonologically correct choice.
        # Comment out the line below to preserve 'v' instead.
        # (r"v", "b"),
        # -ille- → y  (fille, famille → fiye, famiye)
        (r"ill(?=[aeiou])", "ll"),
        (r"ille$", "ille"),
        (r"ill$", "ill"),
        (r"v", "vv"), # temporary placeholder to protect 'v' from being replaced by 'b' in the next pass
        # h (always silent in French) → delete (but NOT the ch placeholder)
        (r"(?<!\x01C)h(?!\x01)", ""),
    ]

    # ------------------------------------------------------------------
    # Pass 5: Word-final silent consonant deletion
    # Delete silent word-final consonants (applied per token).
    # ------------------------------------------------------------------
    # Pattern: word ends in one of these consonants (often silent in French)
    SILENT_FINAL_PATTERN = re.compile(
        r"([aeiouâàäéèêëîïôùûü])"      # preceded by a vowel
        r"[tdsxzp]$",                   # followed by silent consonant at end
        re.IGNORECASE
    )
    # Also: infinitive -er → -e  (pronounced /e/)
    INFINITIVE_ER = re.compile(r"er$", re.IGNORECASE)
    # -ez → -e  (/e/)
    EZ_ENDING = re.compile(r"ez$", re.IGNORECASE)
    # -ent (3rd pl) → -en (nasal) or just strip t
    ENT_ENDING = re.compile(r"ent$", re.IGNORECASE)

    # ------------------------------------------------------------------
    # Pass 6: Double consonant simplification
    # ------------------------------------------------------------------
    DOUBLE_CONSONANT = re.compile(r"([bcdfgklmnprst])\1", re.IGNORECASE)

    # ------------------------------------------------------------------
    # Internal compile helper
    # ------------------------------------------------------------------

    @staticmethod
    def _compile(rules: list[tuple[str, str]]) -> list[tuple[re.Pattern, str]]:
        return [(re.compile(pat, re.IGNORECASE), repl) for pat, repl in rules]

    def __init__(self) -> None:
        self._nasal   = self._compile(self.NASAL_RULES)
        self._vowel   = self._compile(self.VOWEL_RULES)
        self._cluster = self._compile(self.CONSONANT_CLUSTER_RULES)
        self._single  = self._compile(self.SINGLE_CHAR_RULES)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def convert(self, text: str) -> str:
        """
        Convert a French string (word, phrase, or sentence) to its
        Hispanicized form.  Preserves original capitalization pattern.
        """
        words = text.split()
        converted = [self._convert_word(w) for w in words]
        return " ".join(converted).replace("'", "")

    def convert_with_steps(self, word: str) -> list[tuple[str, str]]:
        """
        Return a step-by-step trace of the conversion for a single token.
        Returns a list of (stage_name, result) tuples.
        """
        steps: list[tuple[str, str]] = [("input", word)]
        w = _norm(word.strip(".,;:!?\"'()[]"))

        w = self._apply_pass(w, self._nasal,   "nasal vowels");   steps.append(("pass 1: nasal vowels", w))
        w = self._apply_pass(w, self._vowel,   "vowel digraphs"); steps.append(("pass 2: vowel digraphs", w))
        w = self._apply_pass(w, self._cluster, "consonant clusters"); steps.append(("pass 3: consonant clusters", w))
        w = self._apply_pass(w, self._single,  "single chars");   steps.append(("pass 4: single chars", w))
        w = self._pass5_silent_finals(w);   steps.append(("pass 5: silent finals", w))
        w = self._pass6_doubles(w);         steps.append(("pass 6: double consonants", w))
        w = self._pass7_cleanup(w);         steps.append(("pass 7: cleanup", w))

        return steps

    # ------------------------------------------------------------------
    # Internal passes
    # ------------------------------------------------------------------

    def _convert_word(self, token: str) -> str:
        """Convert a single whitespace-delimited token, preserving casing."""
        # Strip punctuation for processing, reattach afterward
        prefix, core, suffix = self._split_punct(token)
        original_core = core
        w = _norm(core)

        w = self._apply_pass(w, self._nasal)
        w = self._apply_pass(w, self._vowel)
        w = self._apply_pass(w, self._cluster)
        w = self._apply_pass(w, self._single)
        w = self._pass5_silent_finals(w)
        w = self._pass6_doubles(w)
        w = self._pass7_cleanup(w)
        w = self._restore_case(original_core, w)

        return prefix + w + suffix

    @staticmethod
    def _apply_pass(
        text: str,
        rules: list[tuple[re.Pattern, str]],
        _label: str = "",
    ) -> str:
        for pattern, repl in rules:
            text = pattern.sub(repl, text)
        return text

    def _pass5_silent_finals(self, w: str) -> str:
        # Infinitive -er → -e
        w = self.INFINITIVE_ER.sub("e", w)
        # -ez → -e
        w = self.EZ_ENDING.sub("e", w)
        # -ent → -en (verb ending)
        w = self.ENT_ENDING.sub("en", w)
        # Vowel + silent stop/sibilant at end
        w = self.SILENT_FINAL_PATTERN.sub(r"\1", w)
        return w

    def _pass6_doubles(self, w: str) -> str:
        return self.DOUBLE_CONSONANT.sub(r"\1", w)

    @staticmethod
    def _pass7_cleanup(w: str) -> str:
        # Restore protected 'ch' placeholder
        w = w.replace("\x01CH\x01", "ch")
        # Collapse any accidental triple+ of same vowel
        w = re.sub(r"([aeiou])\1{2,}", r"\1\1", w)
        # Remove stray French diacritics that survived (preserve ñ for Spanish)
        cleaned = []
        for ch in unicodedata.normalize("NFD", w):
            # Keep n-tilde combining mark so ñ is preserved
            if unicodedata.category(ch) == "Mn":
                if cleaned and cleaned[-1] in ("n", "N") and unicodedata.name(ch, "") == "COMBINING TILDE":
                    pass  # keep this combining mark → will form ñ
                else:
                    continue
            cleaned.append(ch)
        w = unicodedata.normalize("NFC", "".join(cleaned))
        # Collapse doubled vowels created by rule interactions (oo → o, etc.)
        w = re.sub(r"([aeiou])\1", r"\1", w)
        return w

    @staticmethod
    def _split_punct(token: str) -> tuple[str, str, str]:
        """Split leading/trailing punctuation from a token."""
        m = re.match(r"^([^\w\u00C0-\u024F]*)([\w\u00C0-\u024F''-]*)([^\w\u00C0-\u024F]*)$", token)
        if m:
            return m.group(1), m.group(2), m.group(3)
        return "", token, ""

    @staticmethod
    def _restore_case(original: str, converted: str) -> str:
        """
        Restore capitalization from original to converted string.
        - All-caps → all-caps
        - Title-case → title-case
        - Otherwise → as-is (already lowercase from _norm)
        """
        if not original:
            return converted
        if original.isupper():
            return converted.upper()
        if original[0].isupper():
            return converted.capitalize()
        return converted


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_trace(word: str, hispanicizer: FrenchHispanicizer) -> None:
    steps = hispanicizer.convert_with_steps(word)
    print(f"\n{'─'*50}")
    print(f"  Word: {word}")
    print(f"{'─'*50}")
    for stage, result in steps:
        print(f"  {stage:<30} →  {result}")
    print(f"{'─'*50}\n")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Hispanicize French orthography."
    )
    parser.add_argument(
        "word", nargs="?", help="Single French word or phrase to convert."
    )
    parser.add_argument(
        "-f", "--file", help="Input file: one French word/line."
    )
    parser.add_argument(
        "-t", "--trace", action="store_true",
        help="Show step-by-step conversion trace."
    )
    args = parser.parse_args()

    h = FrenchHispanicizer()

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            if args.trace:
                _print_trace(line, h)
            else:
                print(h.convert(line))

    elif args.word:
        if args.trace:
            _print_trace(args.word, h)
        else:
            print(h.convert(args.word))

    else:
        # Interactive mode
        print("French → Hispanicized French  (type 'quit' to exit)")
        print("Append  -t  after input to see step trace, e.g.:  château -t\n")
        while True:
            try:
                raw = input("French > ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if raw.lower() in ("quit", "exit", "q"):
                break
            if not raw:
                continue
            trace = raw.endswith("-t")
            word  = raw[:-2].strip() if trace else raw
            if trace:
                _print_trace(word, h)
            else:
                print(" →", h.convert(word))


# ---------------------------------------------------------------------------
# Quick demo when run directly without arguments
# ---------------------------------------------------------------------------

DEMO_WORDS = [
    "château", "liberté", "jardin", "feuille", "homme",
    "bonjour", "nuit", "champagne", "fauteuil", "bœuf",
    "nation", "chanter", "idée", "café", "beaux",
]

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No args: show demo, then enter interactive mode
        h = FrenchHispanicizer()
        print("\n=== Demo: Worked Examples ===\n")
        print(f"  {'French':<20} {'Hispanicized'}")
        print(f"  {'─'*20} {'─'*20}")
        for word in DEMO_WORDS:
            print(f"  {word:<20} {h.convert(word)}")
        print()
        print("(Run with  -t  flag for step traces, or  -h  for help)\n")
        main()
    else:
        main()