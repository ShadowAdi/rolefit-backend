"""
cl_style_minimal.py  —  MINIMAL cover letter styles
──────────────────────────────────────────────────────
Visual identity:
  • Name LEFT-aligned, large (24pt), pure near-black — no colour at all
  • Contact left-aligned below name, separated by  ·
  • NO horizontal rule — just generous whitespace
  • Date right-aligned (floats to the right margin)
  • Company block: plain, no bold, just uppercase small label above
  • Salutation: regular weight (not bold)
  • Body: 11pt, very generous leading (16pt) — airy, readable
  • Sign-off: plain, same as body
"""

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_RIGHT

MINI_DARK = HexColor("#1a1a1a")
MINI_SUBTEXT = HexColor("#777777")
MINI_RULE = HexColor("#e0e0e0")


def _build_cl_styles_minimal() -> dict[str, ParagraphStyle]:
    def s(name, **kw) -> ParagraphStyle:
        defaults = dict(
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            textColor=MINI_DARK,
            spaceAfter=0,
            spaceBefore=0,
        )
        defaults.update(kw)
        return ParagraphStyle(name=name, **defaults)

    return {
        # Large, left-aligned, pure near-black — zero colour
        "name": s(
            "mini_cl_name",
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=MINI_DARK,
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        # Left-aligned, muted, small — separated by · in builder
        "contact": s(
            "mini_cl_contact",
            fontSize=9,
            leading=12,
            textColor=MINI_SUBTEXT,
            alignment=TA_LEFT,
            spaceAfter=16,
        ),
        # Date right-aligned — floats to margin
        "date": s(
            "mini_cl_date",
            fontSize=9.5,
            leading=13,
            textColor=MINI_SUBTEXT,
            alignment=TA_RIGHT,
            spaceAfter=6,
        ),
        # Company block: no bold — just the name and role, muted
        "company_block": s(
            "mini_cl_company",
            fontSize=10,
            leading=14,
            textColor=MINI_DARK,
            alignment=TA_LEFT,
            spaceAfter=16,
        ),
        # Salutation: regular weight (minimal uses plain text, not bold)
        "salutation": s(
            "mini_cl_salutation",
            fontSize=11,
            leading=14,
            textColor=MINI_DARK,
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        # Body: generous leading for readability
        "body": s(
            "mini_cl_body",
            fontSize=11,
            leading=16.5,
            textColor=MINI_DARK,
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        # Sign-off: plain, same size as body
        "signoff": s(
            "mini_cl_signoff",
            fontSize=11,
            leading=14,
            textColor=MINI_DARK,
            alignment=TA_LEFT,
            spaceAfter=32,
        ),
        "signed_name": s(
            "mini_cl_signed_name",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=MINI_DARK,
            alignment=TA_LEFT,
        ),
    }
