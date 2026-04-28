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
