import io
import re
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    Flowable,
    HRFlowable,
)
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.colors import HexColor
from app.core.resume_colors import (
    BOLD_BG,
    BOLD_WHITE,
    BOLD_ACCENT,
    BOLD_DARK,
    BOLD_SUBTEXT,
    BOLD_RULE,
)

TECH_COLOR = HexColor("#444444")
DARK_GRAY = HexColor("#3a3a3a")


def build_styles_bold() -> dict:
    base = getSampleStyleSheet()

    def s(name, **kw) -> ParagraphStyle:
        defaults = dict(
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            textColor=BOLD_DARK,
            spaceAfter=0,
            spaceBefore=0,
        )
        defaults.update(kw)
        return ParagraphStyle(name=name, parent=base["Normal"], **defaults)

    return {
        "name": s(
            "bold_name",
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=BOLD_WHITE,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "title": s(
            "bold_title",
            fontSize=11,
            textColor=HexColor("#c0c8f0"),
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "contact": s(
            "bold_contact",
            fontSize=8.5,
            leading=11,
            textColor=HexColor("#aab0cc"),
            alignment=TA_CENTER,
            spaceAfter=0,
        ),
        "role": s(
            "bold_role",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=BOLD_DARK,
        ),
        "company_meta": s(
            "bold_company_meta",
            fontSize=8.5,
            leading=11,
            textColor=BOLD_SUBTEXT,
            spaceAfter=1,
        ),
        "bullet": s(
            "bold_bullet",
            fontSize=9.5,
            leading=12,
            leftIndent=10,
            firstLineIndent=-10,
            spaceAfter=1,
        ),
        "skill_category": s(
            "bold_skill_cat",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=11,
            textColor=BOLD_ACCENT,
        ),
        "skill_items": s("bold_skill_items", fontSize=8.5, leading=11),
        "summary": s("bold_summary", fontSize=9.5, leading=13, spaceAfter=4),
        "pub": s("bold_pub", fontSize=9, leading=12, spaceAfter=1),
        "edu_desc": s(
            "bold_edu_desc",
            fontSize=9,
            leading=11,
            textColor=DARK_GRAY,
            spaceAfter=1,
        ),
        "proj_tech": s(
            "bold_proj_tech",
            fontSize=8.5,
            leading=11,
            textColor=TECH_COLOR,
            fontName="Helvetica-Oblique",
            spaceAfter=2,
        ),
    }
