import re
from spellchecker import SpellChecker
from difflib import get_close_matches

spell = SpellChecker(language="es")


# TODO: convert in english
def corregir_comodin(palabra):
    palabra_lower = palabra.lower()

    if "*" not in palabra_lower:
        correccion = spell.correction(palabra_lower)
        return correccion if correccion else palabra_lower

    palabra_base = palabra_lower.replace("*", "")

    candidatos = get_close_matches(
        palabra_base, spell.word_frequency.keys(), n=3, cutoff=0.6
    )

    if candidatos:
        return candidatos[0]
    else:
        return palabra_base


def clean_text_spell(texto):
    texto_limpio = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s.,]", "", texto)
    texto_limpio = re.sub(r"\s+", " ", texto_limpio).strip()

    palabras = texto_limpio.split()
    palabras_corregidas = [corregir_comodin(p) for p in palabras]

    texto_final = " ".join(palabras_corregidas)

    texto_final = ". ".join([p.capitalize() for p in texto_final.split(". ")])

    return texto_final
