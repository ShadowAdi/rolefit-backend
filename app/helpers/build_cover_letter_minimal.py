"""
build_cover_letter_pdf_minimal.py  —  MINIMAL cover letter template
─────────────────────────────────────────────────────────────────────
Structural differences from Classic:
  • Name LEFT-aligned (24pt, near-black) — no accent colour
  • Contact LEFT-aligned below name, separated by  ·  (not |)
  • NO horizontal rule at all — replaced by generous Spacer
  • Date RIGHT-aligned (floats to right margin)
  • Company block: plain text, small ALL-CAPS label "TO:" above it
  • Salutation: regular weight (not bold)
  • Body: 11pt, leading 16.5 — spacious and readable
  • Wider margins (1.0in) for a letter-style feel
"""

import io
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from app.schema.CoverLetterData import CoverLetterData
from app.utils.style.cl_style_minimal import _build_cl_styles_minimal, MINI_SUBTEXT
from .build_pdf import fit_single_page


def build_cover_letter_pdf_minimal(data: CoverLetterData) -> bytes:
    buff = io.BytesIO()
    M = 1.0 * inch  # wider margins → letter-style feel

    doc = SimpleDocTemplate(
        buff,
        pagesize=letter,
        leftMargin=M,
        rightMargin=M,
        topMargin=0.70 * inch,
        bottomMargin=0.65 * inch,
    )

    styles = _build_cl_styles_minimal()
    story = []

    candidate = data.candidate
    company = data.company

    if candidate.name:
        story.append(Paragraph(candidate.name, styles["name"]))

    contact_parts = []
    for field in [candidate.email, candidate.phone, candidate.location]:
        if field and field.strip():
            contact_parts.append(field.strip().replace("&", "&amp;"))
    if candidate.linkedin and candidate.linkedin.strip():
        url = candidate.linkedin.strip().replace("&", "&amp;")
        contact_parts.append(
            f'<link href="{url}"><font color="#555555">LinkedIn</font></link>'
        )
    if contact_parts:
        story.append(Paragraph("  ·  ".join(contact_parts), styles["contact"]))

    story.append(Spacer(1, 20))

    if data.date:
        story.append(Paragraph(data.date, styles["date"]))
        story.append(Spacer(1, 14))

    if company.name or company.role:
        to_label_style = ParagraphStyle(
            "mini_to",
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=MINI_SUBTEXT,
            spaceAfter=3,
        )
        story.append(Paragraph("TO", to_label_style))
        lines = []
        if company.name:
            lines.append(company.name.replace("&", "&amp;"))
        if company.role:
            lines.append(f"Re: {company.role} Position")
        story.append(Paragraph("<br/>".join(lines), styles["company_block"]))
        story.append(Spacer(1, 4))

    story.append(Paragraph("Dear Hiring Manager,", styles["salutation"]))

    for key in ("opening", "body1", "body2", "closing"):
        text = getattr(data.paragraphs, key, "").strip()
        if not text:
            continue
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(safe, styles["body"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph(data.sign_off + ",", styles["signoff"]))
    if candidate.name:
        story.append(Paragraph(candidate.name, styles["signed_name"]))

    doc.build(fit_single_page(story, doc))
    buff.seek(0)
    return buff.read()
