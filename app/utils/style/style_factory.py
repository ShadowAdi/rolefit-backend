from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from app.core.resume_colors import BLACK, ACCENT, SUBTEXT, RULE
from reportlab.platypus import Paragraph, HRFlowable
from reportlab.lib.colors import HexColor


DARK_GRAY = HexColor("#3a3a3a")
TECH_COLOR = HexColor("#1c1d1e")


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()

    def s(name, **kw) -> ParagraphStyle:
        defaults = dict(
            fontName="Helvetica",
            fontSize=9.5,
            leading=10,
            textColor=BLACK,
            spaceAfter=0,
            spaceBefore=0,
        )
        defaults.update(kw)
        return ParagraphStyle(name=name, parent=base["Normal"], **defaults)

    return {
        "name": s(
            "name",
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=ACCENT,
            alignment=TA_CENTER,
        ),
        "title": s(
            "title", fontSize=12, textColor=SUBTEXT, alignment=TA_CENTER, spaceAfter=1
        ),
        "contact": s(
            "contact",
            fontSize=10,
            leading=10,
            textColor=SUBTEXT,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "section_header": s(
            "section_header",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=ACCENT,
            spaceBefore=4,
            spaceAfter=3,
            borderPadding=(0, 0, 2, 0),  # bottom padding for the underline
        ),
        "role": s(
            "role", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=BLACK
        ),
        "company_meta": s(
            "company_meta", fontSize=8.5, leading=11, textColor=SUBTEXT, spaceAfter=1
        ),
        "bullet": s(
            "bullet",
            fontSize=10,
            leading=12,
            leftIndent=10,
            firstLineIndent=-10,
            spaceAfter=1,
        ),
        "skill_category": s(
            "skill_cat",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=11,
            textColor=SUBTEXT,
        ),
        "skill_items": s("skill_items", fontSize=8.5, leading=11),
        "summary": s("summary", fontSize=10, leading=12, spaceAfter=2),
        "pub": s("pub", fontSize=9, leading=12, spaceAfter=1),
        # Education description: dark gray (near-black) instead of blue-gray SUBTEXT
        "edu_desc": s(
            "edu_desc", fontSize=9.5, leading=11, textColor=DARK_GRAY, spaceAfter=1
        ),
        # Project tech stack: accent-tinted dark blue, italic, slightly smaller
        "proj_tech": s(
            "proj_tech",
            fontSize=8.5,
            leading=11,
            textColor=TECH_COLOR,
            fontName="Helvetica-Oblique",
            spaceAfter=1,
        ),
    }


def section_header(text: str, styles: dict) -> list:
    """Section header with a clean thin HR rule below — no double borders."""
    return [
        Paragraph(text.upper(), styles["section_header"]),
        HRFlowable(
            width="100%",
            thickness=0.4,
            color=ACCENT,
            spaceAfter=3,
            spaceBefore=0,
        ),
    ]


def bullet_para(text: str, styles: dict) -> Paragraph:
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(f"• {safe}", styles["bullet"])
