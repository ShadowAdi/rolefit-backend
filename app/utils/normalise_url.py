import re
from urllib.parse import urlparse, parse_qs


def _normalise_url(url: str) -> str:
    parsed = urlparse(url=url)

    if "drive.google.com" in parsed.netloc:
        m = re.search(r"/file/d/([^/]+)", parsed.path)
        if m:
            file_id = m.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"

        qs = parse_qs(parsed.query)
        if "id" in qs:
            file_id = qs["id"][0]
            return f"https://drive.google.com/uc?export=download&id={file_id}"

        return url
