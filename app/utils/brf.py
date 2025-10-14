import subprocess
import io


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


def text_to_brf_file(text: str):
    brf_content = translate_to_brf_content(text)

    brf_bytes = io.BytesIO()
    brf_bytes.write(brf_content.encode("utf-8"))
    brf_bytes.seek(0)

    return brf_bytes
