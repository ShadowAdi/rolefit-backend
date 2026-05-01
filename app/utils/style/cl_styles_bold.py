"""
cl_style_bold.py  —  BOLD cover letter styles
───────────────────────────────────────────────
Visual identity:
  • Name LEFT-aligned, large (26pt), near-black — no centered accent colour
  • Contact RIGHT-aligned on same row as name (handled via Table in builder)
  • Dark navy top bar (full-width rectangle) containing name + contact
  • Section divider: vivid red-pink (#e8445a) 1.5pt rule
  • Company block has red-pink left border (drawn via Flowable in builder)
  • Body text slightly smaller (10pt) for a denser, professional feel
  • Sign-off uses the accent colour
"""

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

BOLD_BG = HexColor("#1b1f3b")  # dark navy header bg
BOLD_WHITE = HexColor("#ffffff")
BOLD_LIGHT = HexColor("#c0c8f0")  # soft lavender — contact on dark bg
BOLD_ACCENT = HexColor("#e8445a")  # red-pink
BOLD_DARK = HexColor("#1a1a1a")  # near-black body
BOLD_SUBTEXT = HexColor("#555555")


def _build_cl_styles_bold() -> dict[str, ParagraphStyle]:
    def s(name, **kw) -> ParagraphStyle:
        defaults = dict(
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            textColor=BOLD_DARK,
            spaceAfter=0,
            spaceBefore=0,
        )
        defaults.update(kw)
        return ParagraphStyle(name=name, **defaults)

    return {
        # Renders ON the dark navy header → white text
        "name": s(
            "bold_cl_name",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=BOLD_WHITE,
            alignment=TA_LEFT,
            spaceAfter=1,
        ),
        "contact": s(
            "bold_cl_contact",
            fontSize=8.5,
            leading=12,
            textColor=BOLD_LIGHT,
            alignment=TA_RIGHT,
            spaceAfter=0,
        ),
        # Body elements (white background)
        "date": s(
            "bold_cl_date",
            fontSize=10,
            leading=13,
            textColor=BOLD_SUBTEXT,
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        "company_block": s(
            "bold_cl_company",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=BOLD_DARK,
            alignment=TA_LEFT,
            spaceAfter=14,
        ),
        "salutation": s(
            "bold_cl_salutation",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=BOLD_DARK,
            alignment=TA_LEFT,
            spaceAfter=10,
        ),
        "body": s(
            "bold_cl_body",
            fontSize=10,
            leading=15,
            textColor=BOLD_DARK,
            alignment=TA_LEFT,
            spaceAfter=10,
        ),
        "signoff": s(
            "bold_cl_signoff",
            fontSize=10.5,
            leading=14,
            textColor=BOLD_ACCENT,
            alignment=TA_LEFT,
            spaceAfter=28,
        ),
        "signed_name": s(
            "bold_cl_signed_name",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=BOLD_DARK,
            alignment=TA_LEFT,
        ),
    }
