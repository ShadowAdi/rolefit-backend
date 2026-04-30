import io
import re
from reportlab.platypus import Flowable
from reportlab.lib.enums import TA_LEFT  # ← LEFT, not CENTER
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
        # ── Structurally different from Classic ──────────────────────────
        # Classic: name centered, 18pt, ACCENT colour
        # Minimalist: name LEFT-aligned, 26pt, near-black — no accent
        "name": s(
            "mini_name",
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=30,
            textColor=MINI_BLACK,  # near-black, not accent blue
            alignment=TA_LEFT,  # LEFT, not centered
            spaceAfter=1,
        ),
        # Classic: title centered
        # Minimalist: title left, slightly muted, sits directly under name
        "title": s(
            "mini_title",
            fontSize=10.5,
            leading=13,
            textColor=MINI_SUBTEXT,
            alignment=TA_LEFT,
            spaceAfter=3,
        ),
        # Classic: contact centered, separated by |
        # Minimalist: contact left, separated by · (set in pdf builder)
        "contact": s(
            "mini_contact",
            fontSize=8.5,
            leading=11,
            textColor=MINI_SUBTEXT,
            alignment=TA_LEFT,
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
        # Classic: bullets 10pt leading 12 — compact
        # Minimalist: bullets 9pt leading 14 — airy
        "bullet": s(
            "mini_bullet",
            fontSize=9,
            leading=14,
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
        "summary": s("mini_summary", fontSize=9.5, leading=14, spaceAfter=4),
        "pub": s("mini_pub", fontSize=9, leading=12, spaceAfter=1),
        "edu_desc": s(
            "mini_edu_desc",
            fontSize=9,
            leading=11,
            textColor=DARK_GRAY,
            spaceAfter=1,
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


class MiniSectionHeader(Flowable):
    """
    Structurally different from Classic SectionHeaderFlowable:
      - Rule is BELOW the label (not above)
      - Plain Helvetica 7.5pt (not bold)
      - SPACE_BEFORE = 14pt (vs Classic 10pt) — more breathing room
      - No accent colour — pure gray
      - drawString called ONCE (original had duplicate)
    """

    FONT = "Helvetica"
    FONT_SIZE = 7.5
    RULE_T = 0.4
    SPACE_BEFORE = 14
    SPACE_AFTER = 6
    RULE_GAP = 3

    def __init__(self, text: str):
        super().__init__()
        self.text = text.upper()
        self._height = (
            self.SPACE_BEFORE
            + self.FONT_SIZE
            + self.RULE_GAP
            + self.RULE_T
            + self.SPACE_AFTER
        )

    def wrap(self, aw, ah):
        self._width = aw
        return aw, self._height

    def draw(self):
        c = self.canv
        rule_y = self.SPACE_AFTER
        text_y = rule_y + self.RULE_T + self.RULE_GAP

        # Label — drawn ONCE
        c.setFont(self.FONT, self.FONT_SIZE)
        c.setFillColor(MINI_SUBTEXT)
        c.drawString(0, text_y, self.text)

        # Rule BELOW the label
        c.setStrokeColor(MINI_RULE)
        c.setLineWidth(self.RULE_T)
        c.line(0, rule_y, self._width, rule_y)


def section_header_minimalist(text: str, styles: dict) -> list:
    return [MiniSectionHeader(text=text)]


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
