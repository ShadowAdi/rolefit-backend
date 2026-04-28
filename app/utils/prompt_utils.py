MONTH_MAP = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def _fmt_date(month, year, fallback: str = "Present") -> str:
    if year and month:
        return f"{MONTH_MAP.get(int(month), '')} {year}"
    if year:
        return str(year)
    return fallback


_BLOCKED_SPEC_KEYWORDS = [
    "color",
    "colour",
    "theme",
    "font",
    "layout",
    "margin",
    "padding",
    "template",
    "border",
    "background",
    "page size",
    "column",
    "sidebar",
    "header style",
    "footer",
]


def _sanitize_user_specifications(raw: str | None) -> str | None:
    if not raw or not raw.strip():
        return None
    lines = raw.strip().splitlines()
    allowed = [
        line.strip()
        for line in lines
        if not any(kw in line.lower() for kw in _BLOCKED_SPEC_KEYWORDS)
    ]
    cleaned = "\n".join(l for l in allowed if l)
    return cleaned if cleaned else None


def _label_links(links) -> list[str]:
    if not links:
        return []
    label_map = {
        "github": "GitHub",
        "live": "Live",
        "vercel": "Live",
        "demo": "Demo",
        "url": "Link",
        "website": "Website",
        "paper": "Paper",
        "arxiv": "arXiv",
    }
    labelled = []
    if isinstance(links, dict):
        for key, url in links.items():
            if url:
                label = label_map.get(key.lower(), key.capitalize())
                labelled.append(f"{label}::{url}")
    elif isinstance(links, list):
        default_labels = ["GitHub", "Live", "Demo", "Link"]
        for i, url in enumerate(links):
            if url:
                label = default_labels[i] if i < len(default_labels) else "Link"
                labelled.append(f"{label}::{url}")
    return labelled


def _estimate_years(experiences: list) -> float:
    total = 0
    for exp in experiences:
        start = int(exp.get("start_year", 0) or 0)
        end = int(exp.get("end_year", 0) or 0)
        if start and end:
            total += max(0, end - start)
    return total


def _is_ml_role(jd: dict) -> bool:
    ml_keywords = {
        "ml",
        "machine learning",
        "deep learning",
        "ai",
        "data science",
        "nlp",
        "llm",
    }
    text = (jd.get("role_name", "") + " " + " ".join(jd.get("tech_stack", []))).lower()
    return any(kw in text for kw in ml_keywords)


_BLOCKED_SPEC_KEYWORDS = [
    "color",
    "colour",
    "theme",
    "font",
    "layout",
    "margin",
    "padding",
    "template",
    "border",
    "background",
    "page size",
    "column",
    "sidebar",
    "header style",
    "footer",
    "section order",
    "reorder sections",
    "move section",
    "remove section",
    "add section",
]


def _sanitize_user_specifications(raw: str | None) -> str | None:
    """
    Strip out any layout/color/structural requests from user_specifications.
    Returns cleaned text, or None if nothing useful remains.
    """
    if not raw or not raw.strip():
        return None

    lines = raw.strip().splitlines()
    allowed_lines = []

    for line in lines:
        lower = line.lower()
        if any(kw in lower for kw in _BLOCKED_SPEC_KEYWORDS):
            continue
        allowed_lines.append(line.strip())

    cleaned = "\n".join(l for l in allowed_lines if l)
    return cleaned if cleaned else None
