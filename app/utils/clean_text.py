import re


def _clean_text(raw: str) -> str:
    text = raw
    LIGATURES = {
        "\ufb00": "ff",
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\ufb03": "ffi",
        "\ufb04": "ffl",
        "\ufb05": "st",
        "\ufb06": "st",
        "\u2019": "'",  # right single quotation mark
        "\u2018": "'",  # left single quotation mark
        "\u201c": '"',  # left double quotation mark
        "\u201d": '"',  # right double quotation mark
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2022": "*",  # bullet
        "\u2023": "*",  # triangular bullet
        "\u25cf": "*",  # black circle
        "\u00a0": " ",  # non-breaking space
        "\u200b": "",  # zero-width space
        "\u200c": "",  # zero-width non-joiner
        "\u200d": "",  # zero-width joiner
        "\ufeff": "",  # BOM
    }

    for glyph, replacement in LIGATURES.items():
        text = text.replace(glyph, replacement)

    text = re.sub(r"[^\x09\x0a\x0d\x20-\x7e\u00a1-\uFFFF]", "", text)

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    text = re.sub(r"^[\-=_·•*~]{3,}\s*$", "", text, flags=re.MULTILINE)

    text = re.sub(r"\n{3,}", "\n\n", text)

    text = re.sub(r"[ \t]{2,}", " ", text)

    text = text.strip()

    return text
