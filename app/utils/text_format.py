import re
from spellchecker import SpellChecker
from difflib import get_close_matches

spell = SpellChecker(language="es")


def correct_text(text):
    word_lower = text.lower()

    if "*" not in word_lower:
        correction = spell.correction(word_lower)
        return correction if correction else word_lower

    base_word = word_lower.replace("*", "")

    candidates = get_close_matches(
        base_word, spell.word_frequency.keys(), n=3, cutoff=0.6
    )

    if candidates:
        return candidates[0]
    else:
        return base_word


def clean_text_spell(text):
    clean_text = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s.,]", "", text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    words = clean_text.split()
    corrected_words = [correct_text(w) for w in words]

    final_text = " ".join(corrected_words)

    final_text = ". ".join([w.capitalize() for w in final_text.split(". ")])

    return final_text
