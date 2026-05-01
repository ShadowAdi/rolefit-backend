import io
from reportlab.lib.styles import ParagraphStyle
from app.core.resume_colors import BLACK, ACCENT, SUBTEXT
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def _build_cl_styles() -> dict[str, ParagraphStyle]:
    def s(name, **kw) -> ParagraphStyle:
        defaults = dict(
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            textColor=BLACK,
            spaceAfter=0,
            spaceBefore=0,
        )
        defaults.update(kw)
        return ParagraphStyle(name=name, **defaults)

    return {
        "name": s(
            "cl_name",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=ACCENT,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "contact": s(
            "cl_contact",
            fontSize=9,
            leading=12,
            textColor=SUBTEXT,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "date": s(
            "cl_date",
            fontSize=10,
            leading=13,
            textColor=SUBTEXT,
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        "company_block": s(
            "cl_company",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=BLACK,
            alignment=TA_LEFT,
            spaceAfter=14,
        ),
        "salutation": s(
            "cl_salutation",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=BLACK,
            alignment=TA_LEFT,
            spaceAfter=10,
        ),
        "body": s(
            "cl_body",
            fontSize=10.5,
            leading=15,
            textColor=BLACK,
            alignment=TA_LEFT,
            spaceAfter=10,
        ),
        "signoff": s(
            "cl_signoff",
            fontSize=10.5,
            leading=14,
            textColor=BLACK,
            alignment=TA_LEFT,
            spaceAfter=28,
        ),
        "signed_name": s(
            "cl_signed_name",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=BLACK,
            alignment=TA_LEFT,
        ),
    }
