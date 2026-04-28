import io
import re

from reportlab.platypus import (
    Paragraph,
    HRFlowable,
    SimpleDocTemplate,
    Spacer,
)
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from app.utils.style.cl_style_factory import _build_cl_styles
from app.core.resume_colors import RULE


def build_cover_letter_pdf(data: dict) -> bytes:
    buff = io.BytesIO()
    M = 0.85 * inch

    doc = SimpleDocTemplate(
        buff,
        pagesize=letter,
        leftMargin=M,
        rightMargin=M,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    styles = _build_cl_styles()
    story = []

    candidate = data.get("candidate", {})
    company = data.get("company", {})
    date_str = data.get("date", "")
    paragraphs = data.get("paragraphs", {})
    sign_off = data.get("sign_off", "Sincerely")

    name = candidate.get("name", "")
    if name:
        story.append(Paragraph(name, styles["name"]))

    contact_parts = []
    for field in [
        candidate.get("email"),
        candidate.get("phone"),
        candidate.get("location"),
    ]:
        if field and field.strip():
            contact_parts.append(field.strip().replace("&", "&amp;"))

    linkedin = candidate.get("linkedin")
    if linkedin and linkedin.strip():
        url = linkedin.strip().replace("&", "&amp;")
        contact_parts.append(
            f'<link href="{url}"><font color="#4a6cf7">LinkedIn</font></link>'
        )

    if contact_parts:
        story.append(Paragraph(" | ".join(contact_parts), styles["contact"]))

    story.append(
        HRFlowable(
            width="100%", thickness=0.5, color=RULE, spaceAfter=12, spaceBefore=0
        )
    )

    if date_str:
        story.append(Paragraph(date_str, styles["date"]))
        story.append(Spacer(1, 6))

    company_name = company.get("name", "")
    role_name = company.get("role", "")

    if company_name or role_name:
        block_lines = []
        if company_name:
            block_lines.append(f"<b>{company_name}</b>")
        if role_name:
            block_lines.append(f"Re: {role_name} Position")
        story.append(Paragraph("<br/>".join(block_lines), styles["company_block"]))

    story.append(Paragraph("Dear Hiring Manager,", styles["salutation"]))

    for key in ("opening", "body1", "body2", "closing"):
        text = paragraphs.get(key, "").strip()
        if not text:
            continue
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(safe, styles["body"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph(sign_off + ",", styles["signoff"]))
    if name:
        story.append(Paragraph(name, styles["signed_name"]))

    doc.build(story)
    buff.seek(0)
    return buff.read()
