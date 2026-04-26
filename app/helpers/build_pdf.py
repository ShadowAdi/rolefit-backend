import io
import re
from app.schema.pdf_resume import ResumeData

from reportlab.platypus import (
    Paragraph,
    HRFlowable,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_RIGHT
from app.core.resume_colors import BLACK, ACCENT, SUBTEXT, RULE
from app.utils.style.style_factory import build_styles, section_header, bullet_para
from reportlab.lib.styles import ParagraphStyle


# ---------------------------------------------------------------------------
# Base bold patterns — metrics and universal tech terms
# ---------------------------------------------------------------------------
_BASE_BOLD = re.compile(
    r"\b("
    # numeric metrics
    r"\d[\d,\.]*\s*%|"
    r"\d[\d,\.]*\+?\s*(?:users|ms|seconds?|minutes?|hours?|days?|months?|requests?|"
    r"records?|events?|transactions?|calls?|endpoints?|services?|nodes?|instances?)|"
    # strong action verbs
    r"Built|Engineered|Developed|Designed|Implemented|Optimized|Reduced|Increased|"
    r"Improved|Automated|Shipped|Led|Architected|Deployed|Migrated|Integrated|"
    r"Launched|Scaled|Delivered|Established|Created|Streamlined|"
    # infra / cloud
    r"REST(?:ful)?|GraphQL|gRPC|Microservices?|CI/CD|Docker|Kubernetes|AWS|GCP|Azure|"
    # databases
    r"PostgreSQL|MongoDB|Redis|Kafka|RabbitMQ|Elasticsearch|TypeORM|Prisma|"
    # frameworks
    r"React|Next\.js|NestJS|Node\.js|FastAPI|Django|Spring Boot|Express|"
    # languages
    r"TypeScript|JavaScript|Python|Go|Golang|Rust|Java|C\+\+|"
    # AI / ML
    r"LLM|GPT|ML|AI|NLP|RAG|fine.tun(?:ing|ed)" r")\b",
    re.IGNORECASE,
)


def _make_bold_pattern(extra_terms: list[str]) -> re.Pattern:
    """Build a combined pattern that also bolds job-specific terms."""
    if not extra_terms:
        return _BASE_BOLD
    # Escape each term for regex, longest first to avoid partial matches
    escaped = sorted(
        [re.escape(t) for t in extra_terms if t and len(t) > 2],
        key=len,
        reverse=True,
    )
    extra_pat = "|".join(escaped)
    combined = _BASE_BOLD.pattern.rstrip(r"\b)") + "|" + extra_pat + r")\b"
    return re.compile(combined, re.IGNORECASE)


def _apply_bold(text: str, pattern: re.Pattern) -> str:
    """HTML-escape text then wrap matched keywords in <b> tags."""
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return pattern.sub(lambda m: f"<b>{m.group(0)}</b>", safe)


# ---------------------------------------------------------------------------
# Header link helpers
# ---------------------------------------------------------------------------

_LINK_LABELS = {
    "github.com": "GitHub",
    "linkedin.com": "LinkedIn",
    "linkedin.in": "LinkedIn",
    "shadowadi.github.io": "Portfolio",  # catch personal portfolio subdomains
    "vercel.app": "Portfolio",
    "netlify.app": "Portfolio",
    "gmail.com": "Gmail",
    "mail.google.com": "Gmail",
    "twitter.com": "Twitter",
    "x.com": "Twitter",
    "behance.net": "Behance",
    "dribbble.com": "Dribbble",
    "medium.com": "Medium",
    "dev.to": "Dev.to",
    "leetcode.com": "LeetCode",
    "hackerrank.com": "HackerRank",
    "kaggle.com": "Kaggle",
    "stackoverflow.com": "Stack Overflow",
}


def _label_for_url(url: str) -> str:
    """Return a short human label for a URL based on its domain."""
    # strip scheme
    clean = re.sub(r"^https?://", "", url).lstrip("www.")
    domain = clean.split("/")[0].lower()
    # exact match
    if domain in _LINK_LABELS:
        return _LINK_LABELS[domain]
    # subdomain match (e.g. shadowadi.github.io)
    for key, label in _LINK_LABELS.items():
        if domain.endswith(key):
            return label
    # fallback: capitalise first segment of domain
    return domain.split(".")[0].capitalize()


def _format_header_links(raw_links: list[str], accent_hex: str = "#4a6cf7") -> str:
    """
    Convert a list of URLs into short labelled hyperlinks separated by ' | '.
    e.g. ["https://github.com/foo", "https://shadowadi.github.io/port/"]
      →  '<link href="...">GitHub</link> | <link href="...">Portfolio</link>'
    """
    parts = []
    seen_labels: dict[str, int] = {}
    for url in raw_links:
        if not url:
            continue
        url_escaped = url.replace("&", "&amp;")
        label = _label_for_url(url)
        # deduplicate: Portfolio 1, Portfolio 2 …
        if label in seen_labels:
            seen_labels[label] += 1
            label = f"{label} {seen_labels[label]}"
        else:
            seen_labels[label] = 1
        parts.append(
            f'<link href="{url_escaped}"><font color="{accent_hex}">{label}</font></link>'
        )
    return " | ".join(parts)


def _render_project_links(
    links: list[str], base_style: ParagraphStyle
) -> "Paragraph | None":
    """Parse 'Label::URL' strings into inline blue hyperlinks."""
    if not links:
        return None
    parts = []
    for entry in links:
        if "::" in entry:
            label, url = entry.split("::", 1)
            url = url.strip().replace("&", "&amp;")
            parts.append(
                f'<link href="{url}"><font color="#4a6cf7">{label.strip()}</font></link>'
            )
        else:
            parts.append(f'<font color="#4a6cf7">{entry.strip()}</font>')

    link_style = ParagraphStyle(
        "proj_links",
        parent=base_style,
        alignment=TA_RIGHT,
        fontSize=8.5,
    )
    return Paragraph("  ".join(parts), link_style)


def build_pdf(data: ResumeData) -> bytes:
    buff = io.BytesIO()
    M = 0.50 * inch

    doc = SimpleDocTemplate(
        buff,
        pagesize=letter,
        leftMargin=M,
        rightMargin=M,
        topMargin=0.40 * inch,
        bottomMargin=0.40 * inch,
    )

    styles = build_styles()
    story = []

    extra_bold_terms: list[str] = []
    if hasattr(data, "job_description") and data.job_description:
        jd = data.job_description
        if hasattr(jd, "company") and jd.company:
            extra_bold_terms.append(jd.company)
        if hasattr(jd, "tech_stack") and jd.tech_stack:
            extra_bold_terms.extend(jd.tech_stack)
        if hasattr(jd, "role_name") and jd.role_name:
            extra_bold_terms.append(jd.role_name)

    bold = _make_bold_pattern(extra_bold_terms)

    h = data.header
    story.append(Paragraph(h.name, styles["name"]))
    if h.title:
        story.append(Paragraph(h.title, styles["title"]))

    contact_text_parts: list[str] = []

    for field in [h.email, h.phone, h.location]:
        if field:
            contact_text_parts.append(field.replace("&", "&amp;"))

    if h.links:
        link_str = _format_header_links(h.links)
        if link_str:
            contact_text_parts.append(link_str)

    if contact_text_parts:
        story.append(Paragraph(" | ".join(contact_text_parts), styles["contact"]))

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=ACCENT,
            spaceBefore=4,
            spaceAfter=8,
            hAlign="CENTER",
        )
    )

    if data.summary:
        story += section_header("Summary", styles)
        story.append(Paragraph(_apply_bold(data.summary, bold), styles["summary"]))
        story.append(Spacer(2, 4))

    if data.skills:
        story += section_header("Skills & Technologies", styles)
        for grp in data.skills:
            if not grp.items:
                continue
            row = [
                Paragraph(grp.category + ":", styles["skill_category"]),
                Paragraph(", ".join(grp.items), styles["skill_items"]),
            ]
            t = Table([row], colWidths=[1.65 * inch, 5.70 * inch])
            t.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                        ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ]
                )
            )
            story.append(t)
        story.append(Spacer(1, 2))

    if data.experience:
        story += section_header("Professional Experience", styles)
        for exp in data.experience:
            date_str = f"{exp.start} – {exp.end}" if exp.start else (exp.end or "")
            company_display = f" · {exp.company}" if exp.company else ""
            emp_display = f", {exp.emp_type}" if exp.emp_type else ""

            role_para = Paragraph(
                f"{exp.role}"
                f"<font color='#242323' size='9'>{company_display}</font>"
                f"<font color='#888888' size='9'>{emp_display}</font>",
                styles["role"],
            )
            header_row = [
                role_para,
                Paragraph(
                    date_str,
                    ParagraphStyle(
                        "date",
                        parent=styles["company_meta"],
                        alignment=TA_RIGHT,
                        fontSize=10,
                    ),
                ),
            ]
            t = Table([header_row], colWidths=[4.5 * inch, 3.0 * inch])
            t.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ]
                )
            )
            story.append(t)

            for b in exp.bullets:
                story.append(Paragraph(f"• {_apply_bold(b, bold)}", styles["bullet"]))
            story.append(Spacer(1, 4))

    if data.projects:
        story += section_header("Projects", styles)
        for proj in data.projects:
            story.append(Paragraph(proj.title, styles["role"]))
            link_para = _render_project_links(proj.links, styles["company_meta"])

            if proj.tech and link_para:
                row = [
                    Paragraph(f"Tech: {proj.tech}", styles["proj_tech"]),
                    link_para,
                ]
                t = Table([row], colWidths=[4.9 * inch, 2.5 * inch])
                t.setStyle(
                    TableStyle(
                        [
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ]
                    )
                )
                story.append(t)
            elif proj.tech:
                story.append(Paragraph(f"Tech: {proj.tech}", styles["proj_tech"]))
            elif link_para:
                story.append(link_para)

            for b in proj.bullets:
                story.append(Paragraph(f"• {_apply_bold(b, bold)}", styles["bullet"]))
            story.append(Spacer(1, 3))

    if data.achievements:
        story += section_header("Achievements & Certifications", styles)
        for ach in data.achievements:
            story.append(Paragraph(f"• {_apply_bold(ach, bold)}", styles["bullet"]))
        story.append(Spacer(1, 2))

    if data.publications:
        story += section_header("Publications", styles)
        for pub in data.publications:
            line = pub.title
            if pub.publisher:
                line += f" — {pub.publisher}"
            if pub.year:
                line += f" ({pub.year})"
            story.append(Paragraph(f"• {_apply_bold(line, bold)}", styles["pub"]))
        story.append(Spacer(1, 2))

    if data.education:
        story += section_header("Education", styles)
        for edu in data.education:
            row = [
                Paragraph(f"<b>{edu.degree}</b>, {edu.institution}", styles["role"]),
                Paragraph(
                    edu.year or "",
                    ParagraphStyle(
                        "edu_year",
                        parent=styles["company_meta"],
                        alignment=TA_RIGHT,
                        fontSize=9,
                    ),
                ),
            ]
            t = Table([row], colWidths=[5.5 * inch, 2.0 * inch])
            t.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ]
                )
            )
            story.append(t)
            if edu.location:
                story.append(Paragraph(edu.location, styles["company_meta"]))
            if hasattr(edu, "description") and edu.description:
                safe = (
                    edu.description.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                story.append(Paragraph(safe, styles["edu_desc"]))

    doc.build(story)
    buff.seek(0)
    return buff.read()
