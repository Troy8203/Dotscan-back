BINARY_TO_LETTER = {
    "100000": "A",
    "110000": "B",
    "100100": "C",
    "100110": "D",
    "100010": "E",
    "110100": "F",
    "110110": "G",
    "110010": "H",
    "010100": "I",
    "010110": "J",
    "101000": "K",
    "111000": "L",
    "101100": "M",
    "101110": "N",
    "110111": "Ñ",
    "101010": "O",
    "111100": "P",
    "111110": "Q",
    "111010": "R",
    "011100": "S",
    "011110": "T",
    "101001": "U",
    "001111": "V",
    "010111": "W",
    "101101": "X",
    "101111": "Y",
    "101011": "Z",
    "111001": "#",
    "010000": ",",
    "001000": ".",
}


def binary_to_letter(binary_code: str) -> str:
    return BINARY_TO_LETTER.get(binary_code.strip(), "?")


def binary_to_braille_char(binary_code: str) -> str:
    try:
        return chr(0x2800 + int(binary_code, 2))
    except ValueError:
        return "⠿"


def binary_to_letter_and_braille(binary_code: str) -> tuple[str, str]:
    letter = binary_to_letter(binary_code)
    braille_char = binary_to_braille_char(binary_code)
    return letter, braille_char
