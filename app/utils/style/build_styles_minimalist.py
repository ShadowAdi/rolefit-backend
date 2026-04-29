import io
import re
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    Flowable,
)
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.colors import HexColor
from app.core.resume_colors import MINI_BLACK, MINI_ACCENT, MINI_SUBTEXT, MINI_RULE

DARK_GRAY = HexColor("#4a4a4a")
TECH_COLOR = HexColor("#777777")


def build_styles_minimalist() -> dict:
    base = getSampleStyleSheet()

    def s(name, **kw) -> ParagraphStyle:
        defaults = dict(
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=MINI_BLACK,
            spaceAfter=0,
            spaceBefore=0,
        )
        defaults.update(kw)
        return ParagraphStyle(name=name, parent=base["Normal"], **defaults)

    return {
        "name": s(
            "mini_name",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=MINI_ACCENT,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "title": s(
            "mini_title",
            fontSize=11,
            textColor=MINI_SUBTEXT,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "contact": s(
            "mini_contact",
            fontSize=8.5,
            leading=11,
            textColor=MINI_SUBTEXT,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "role": s(
            "mini_role",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=MINI_BLACK,
        ),
        "company_meta": s(
            "mini_company_meta",
            fontSize=8.5,
            leading=11,
            textColor=MINI_SUBTEXT,
            spaceAfter=1,
        ),
        "bullet": s(
            "mini_bullet",
            fontSize=9.5,
            leading=13,
            leftIndent=10,
            firstLineIndent=-10,
            spaceAfter=1,
        ),
        "skill_category": s(
            "mini_skill_cat",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=MINI_SUBTEXT,
        ),
        "skill_items": s("mini_skill_items", fontSize=8.5, leading=12),
        "summary": s("mini_summary", fontSize=9.5, leading=13, spaceAfter=4),
        "pub": s("mini_pub", fontSize=9, leading=12, spaceAfter=1),
        "edu_desc": s(
            "mini_edu_desc", fontSize=9, leading=11, textColor=DARK_GRAY, spaceAfter=1
        ),
        "proj_tech": s(
            "mini_proj_tech",
            fontSize=8.5,
            leading=11,
            textColor=TECH_COLOR,
            fontName="Helvetica-Oblique",
            spaceAfter=2,
        ),
    }
