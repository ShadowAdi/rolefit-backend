"""
build_styles_sidebar.py  —  "Sidebar" template styles
───────────────────────────────────────────────────────
Two-column layout:
  LEFT sidebar  (~35% width, slate #1e2235):
    name, title, contact, skills, education
  RIGHT main    (~65% width, white):
    summary, experience, projects, achievements, publications

Sidebar text is always white/light. Main column is dark on white.
Section labels in sidebar: teal accent (#64ffda), tiny, letter-spaced.
Section labels in main: gray uppercase, thin rule below.
"""

import re
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.colors import HexColor

# ── Sidebar palette ────────────────────────────────────────────────────────
SB_BG = HexColor("#1e2235")  # dark slate sidebar bg
SB_WHITE = HexColor("#ffffff")
SB_TEAL = HexColor("#64ffda")  # section label accent
SB_TEXT = HexColor("#a8b2d8")  # normal sidebar text
SB_SUBTEXT = HexColor("#8892b0")  # muted sidebar text
SB_RULE = HexColor("#2d3550")  # sidebar rule color
SB_NAME = HexColor("#cdd6f4")  # name in sidebar (soft white-blue)

# ── Main column palette ────────────────────────────────────────────────────
MAIN_DARK = HexColor("#1a1a1a")
MAIN_SUBTEXT = HexColor("#555555")
MAIN_RULE = HexColor("#e0e0e0")
MAIN_ACCENT = HexColor("#1e2235")  # section label colour = same as sidebar bg
TECH_COLOR = HexColor("#555555")
DARK_GRAY = HexColor("#3a3a3a")


def build_styles_sidebar() -> dict:
    base = getSampleStyleSheet()

    def s(name, **kw) -> ParagraphStyle:
        defaults = dict(
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=MAIN_DARK,
            spaceAfter=0,
            spaceBefore=0,
        )
        defaults.update(kw)
        return ParagraphStyle(name=name, parent=base["Normal"], **defaults)

    return {
        # ── Sidebar styles ─────────────────────────────────────────────────
        "sb_name": s(
            "sb_name",
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=21,
            textColor=SB_WHITE,
            alignment=TA_LEFT,
            spaceAfter=1,
        ),
        "sb_title": s(
            "sb_title",
            fontSize=9,
            leading=12,
            textColor=SB_SUBTEXT,
            alignment=TA_LEFT,
            spaceAfter=8,
        ),
        "sb_contact": s(
            "sb_contact",
            fontSize=8,
            leading=13,
            textColor=SB_TEXT,
            alignment=TA_LEFT,
        ),
        "sb_section": s(
            "sb_section",
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=10,
            textColor=SB_TEAL,
            spaceAfter=4,
            spaceBefore=10,
        ),
        "sb_skill_cat": s(
            "sb_skill_cat",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=SB_NAME,
        ),
        "sb_skill_items": s(
            "sb_skill_items",
            fontSize=7.5,
            leading=11,
            textColor=SB_TEXT,
        ),
        "sb_edu_degree": s(
            "sb_edu_degree",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=SB_NAME,
        ),
        "sb_edu_inst": s(
            "sb_edu_inst",
            fontSize=7.5,
            leading=11,
            textColor=SB_TEXT,
        ),
        "sb_edu_year": s(
            "sb_edu_year",
            fontSize=7.5,
            leading=11,
            textColor=SB_SUBTEXT,
        ),
        # ── Main column styles ─────────────────────────────────────────────
        "main_section": s(
            "main_section",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=MAIN_ACCENT,
            spaceAfter=4,
            spaceBefore=10,
        ),
        "role": s(
            "main_role",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=MAIN_DARK,
        ),
        "company_meta": s(
            "main_meta",
            fontSize=8,
            leading=11,
            textColor=MAIN_SUBTEXT,
            spaceAfter=1,
        ),
        "bullet": s(
            "main_bullet",
            fontSize=8.5,
            leading=12,
            leftIndent=9,
            firstLineIndent=-9,
            spaceAfter=1,
            textColor=MAIN_DARK,
        ),
        "summary": s("main_summary", fontSize=9, leading=13, spaceAfter=4),
        "pub": s("main_pub", fontSize=8.5, leading=12, spaceAfter=1),
        "edu_desc": s(
            "main_edu_desc",
            fontSize=8.5,
            leading=11,
            textColor=DARK_GRAY,
            spaceAfter=1,
        ),
        "proj_tech": s(
            "main_proj_tech",
            fontSize=8,
            leading=11,
            textColor=TECH_COLOR,
            fontName="Helvetica-Oblique",
            spaceAfter=2,
        ),
        # skill_category / skill_items reused in main if needed
        "skill_category": s(
            "main_skill_cat",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=MAIN_SUBTEXT,
        ),
        "skill_items": s("main_skill_items", fontSize=8.5, leading=11),
    }


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
