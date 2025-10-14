import subprocess


def translate_to_brf_content(text: str) -> str:
    result = subprocess.run(
        ["lou_translate", "--forward", "es-g1.ctb"],
        input=text,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def text_to_ascii_braille(text: str) -> str:
    table_path = "es-g1.ctb"
    display_table = "unicode.dis"

    result = subprocess.run(
        ["lou_translate", f"--display-table={display_table}", "--forward", table_path],
        input=text,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()
