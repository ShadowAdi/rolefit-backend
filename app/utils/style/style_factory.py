from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from app.core.resume_colors import BLACK, ACCENT, SUBTEXT, RULE
from reportlab.platypus import Paragraph, HRFlowable


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
            leading=11,
            textColor=ACCENT,
            spaceBefore=4,  # was 8
            spaceAfter=1,  # was 2
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
        "edu_desc": s(
            "edu_desc", fontSize=9.5, leading=11, textColor=SUBTEXT, spaceAfter=1
        ),
    }


def section_header(text: str, styles: dict) -> list:
    return [
        Paragraph(text.upper(), styles["section_header"]),
        HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=3),
    ]


def bullet_para(text: str, styles: dict) -> Paragraph:
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(f"• {safe}", styles["bullet"])
