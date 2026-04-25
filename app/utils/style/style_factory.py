from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from app.core.resume_colors import BLACK, ACCENT, SUBTEXT, RULE, WHITE


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()

    def s(name, **kw) -> ParagraphStyle:
        defaults = dict(
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=BLACK,
            spaceAfter=0,
            spaceBefore=0,
        )
        defaults.update(kw)
        return ParagraphStyle(name=name, parent=base["normal"], **defaults)

    return {
        "name": s(
            "name",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=ACCENT,
            alignment=TA_CENTER,
        ),
        "title": s(
            "title", fontSize=11, textColor=SUBTEXT, alignment=TA_CENTER, spaceAfter=2
        ),
        "contact": s(
            "contact",
            fontSize=8.5,
            textColor=SUBTEXT,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "section_header": s(
            "section_header",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            textColor=ACCENT,
            spaceBefore=8,
            spaceAfter=2,
            textTransform="uppercase",
        ),
        "role": s("role", fontName="Helvetica-Bold", fontSize=10, textColor=BLACK),
        "company_meta": s("company_meta", fontSize=9, textColor=SUBTEXT, spaceAfter=2),
        "bullet": s(
            "bullet",
            fontSize=9.5,
            leading=13,
            leftIndent=10,
            firstLineIndent=-10,
            spaceAfter=1,
        ),
        "skill_category": s(
            "skill_cat", fontName="Helvetica-Bold", fontSize=9, textColor=SUBTEXT
        ),
        "skill_items": s("skill_items", fontSize=9, leading=12),
        "summary": s("summary", fontSize=9.5, leading=13, spaceAfter=4),
        "pub": s("pub", fontSize=9.5, leading=13, spaceAfter=2),
    }
