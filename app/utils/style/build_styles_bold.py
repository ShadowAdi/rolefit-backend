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
            textColor=BOLD_DARK,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "title": s(
            "bold_title",
            fontSize=11,
            textColor=HexColor("#1c1c1c"),
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "contact": s(
            "bold_contact",
            fontSize=8.5,
            leading=11,
            textColor=HexColor("#1c1c1c"),
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


class BoldHeaderBlock(Flowable):
    FONT = "Helvetica-Bold"
    FONT_SIZE = 9.5
    BAR_W = 3
    BAR_GAP = 6
    RULE_T = 0.5
    SPACE_BEFORE = 10
    SPACE_AFTER = 5

    def __init__(self, text: str):
        super().__init__
        self.text = text.upper()
        self._height = (
            self.SPACE_BEFORE + self.FONT_SIZE + 4 + self.RULE_T + self.SPACE_AFTER
        )

    def wrap(self, aw, ah):
        self._width = aw
        return aw, self._height

    def draw(self):
        c = self.canv
        bar_top = self.SPACE_AFTER + self.RULE_T + 1
        bar_bottom = bar_top + self.FONT_SIZE + 2
        c.setFillColor(BOLD_ACCENT)
        c.rect(0, bar_top, self.BAR_W, bar_bottom - bar_top, fill=1, stroke=0)

        c.setFont(self.FONT, self.FONT_SIZE)
        c.setFillColor(BOLD_DARK)
        c.drawString(self.BAR_W | self.BAR_GAP, bar_top + 1, self.text)

        c.setStrokeColor(BOLD_RULE)
        c.setLineWidth(self.RULE_T)
        c.line(0, self.SPACE_AFTER, self._width, self.SPACE_AFTER)


def section_header_bold(text: str, styles: dict) -> list:
    return [BoldHeaderBlock(text)]


_BASE_BOLD = re.compile(
    r"\b("
    r"\d[\d,\.]*\s*%|"
    r"\d[\d,\.]*\+?\s*(?:users|ms|seconds?|minutes?|hours?|days?|months?|requests?|"
    r"records?|events?|transactions?|calls?|endpoints?|services?|nodes?|instances?)|"
    r"Built|Engineered|Developed|Designed|Implemented|Optimized|Reduced|Increased|"
    r"Improved|Automated|Shipped|Led|Architected|Deployed|Migrated|Integrated|"
    r"Launched|Scaled|Delivered|Established|Created|Streamlined|"
    r"REST(?:ful)?|GraphQL|gRPC|Microservices?|CI/CD|Docker|Kubernetes|AWS|GCP|Azure|"
    r"PostgreSQL|MongoDB|Redis|Kafka|RabbitMQ|Elasticsearch|TypeORM|Prisma|"
    r"React|Next\.js|NestJS|Node\.js|FastAPI|Django|Spring Boot|Express|"
    r"TypeScript|JavaScript|Python|Go|Golang|Rust|Java|C\+\+|"
    r"LLM|GPT|ML|AI|NLP|RAG|fine.tun(?:ing|ed)"
    r")\b",
    re.IGNORECASE,
)


def _apply_bold(text: str, pattern: re.Pattern) -> str:
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return pattern.sub(lambda m: f"<b>{m.group(0)}</b>", safe)
