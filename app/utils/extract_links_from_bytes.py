import pdfplumber
import io


def _extract_link_from_bytes(pdf_bytes: bytes) -> list[str]:
    found: list[str] = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            for annot in page.annots or []:
                uri = annot.get("uri")
                if uri and isinstance(uri, str) and uri.startswith("http"):
                    found.append(uri.strip())

    seen: set[str] = set()
    unique: list[str] = []

    for link in found:
        if link not in seen:
            seen.add(link)
            unique.append(link)
    return unique
