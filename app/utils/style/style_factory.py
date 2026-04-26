from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from app.core.resume_colors import BLACK, ACCENT, SUBTEXT, RULE
from reportlab.platypus import Paragraph, Flowable
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth


DARK_GRAY = HexColor("#3a3a3a")
TECH_COLOR = HexColor("#1c1d1e")


class SectionHeaderFlowable(Flowable):
    """
    Draws a section header label (bold, ACCENT colour, uppercased) with a
    hairline rule that runs the full available width — all in a single canvas
    pass so there is exactly ONE line, no duplicates, no gap artefacts.
    """

    FONT = "Helvetica-Bold"
    FONT_SIZE = 10
    RULE_THICKNESS = 0.5
    SPACE_BEFORE = 3  # pts above the whole block
    SPACE_AFTER = 4  # pts below the rule before next element
    GAP = 2  # pts between baseline and rule

    def __init__(self, text: str, accent_color):
        super().__init__()
        self.text = text.upper()
        self.accent = accent_color
        # Tell ReportLab how tall this flowable is
        self._height = (
            self.SPACE_BEFORE
            + self.FONT_SIZE
            # + self.GAP
            # + self.RULE_THICKNESS
            + self.SPACE_AFTER
        )

    def wrap(self, availWidth, availHeight):
        self._width = availWidth
        return availWidth, self._height

    def draw(self):
        c = self.canv
        w = self._width

        # Y positions (ReportLab draws bottom-up)
        rule_y = self.SPACE_AFTER
        text_y = rule_y + self.GAP + self.RULE_THICKNESS

        # Draw label
        c.setFont(self.FONT, self.FONT_SIZE)
        c.setFillColor(self.accent)
        c.drawString(0, text_y, self.text)

        # Draw single hairline rule across full width
        # c.setStrokeColor(self.accent)
        # c.setLineWidth(self.RULE_THICKNESS)
        # c.line(0, rule_y, w, rule_y)


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
            fontSize=9,
            leading=11,
            textColor=SUBTEXT,
            alignment=TA_CENTER,
            spaceAfter=3,
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
            "edu_desc", fontSize=9.5, leading=11, textColor=DARK_GRAY, spaceAfter=1
        ),
        "proj_tech": s(
            "proj_tech",
            fontSize=8.5,
            leading=11,
            textColor=TECH_COLOR,
            fontName="Helvetica-Oblique",
            spaceAfter=1,
        ),
    }


def section_header(text: str, styles: dict, accent=ACCENT) -> list:
    """Return a single SectionHeaderFlowable — one element, one line, no duplicates."""
    return [SectionHeaderFlowable(text, accent)]


def bullet_para(text: str, styles: dict) -> Paragraph:
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(f"• {safe}", styles["bullet"])
