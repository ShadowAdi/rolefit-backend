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
from app.utils.style.build_styles_bold import build_styles_bold
from .build_pdf import _format_header_links
from app.utils.style.build_styles_bold import (
    build_styles_bold,
    _apply_bold,
    section_header_bold,
    BoldHeaderBlock,
)


def build_pdf_bold(data, bold_pattern: re.Pattern = None) -> bytes:
    buff = io.BytesIO()
    M = 0.48 * inch

    # Default pattern: no bold highlighting if not provided
    if bold_pattern is None:
        bold_pattern = re.compile(r"(?!)")  # Pattern that matches nothing

    doc = SimpleDocTemplate(
        buff,
        pagesize=letter,
        leftMargin=M,
        rightMargin=M,
        topMargin=0.0 * inch,
        bottomMargin=0.40 * inch,
    )

    styles = build_styles_bold()
    story = []

    h = data.header
    contact_parts = []

    for field in [h.email, h.phone, h.location]:
        if field:
            contact_parts.append(field.replace("&", "&amp;"))

    if h.links:
        link_str = _format_header_links(h.links, accent_hex="#c0c8f0")
        if link_str:
            contact_parts.append(link_str)

    story.append(Paragraph(h.name, styles["name"]))
    if h.title:
        story.append(Paragraph(h.title, styles["title"]))

    if contact_parts:
        story.append(Paragraph(" | ".join(contact_parts), styles["contact"]))

    story.append(Spacer(1, 8))

    if data.summary:
        story += section_header_bold("Summary", styles)
        story.append(
            Paragraph(_apply_bold(data.summary, bold_pattern), styles["summary"])
        )

    if data.skills:
        story += section_header_bold("Skills & Technologies", styles)
        for grp in data.skills:
            if not grp.items:
                continue
            row = [
                Paragraph(grp.category + ":", styles["skill_category"]),
                Paragraph(", ".join(grp.items), styles["skill_items"]),
            ]
            t = Table([row], colWidths=[1.65 * inch, 5.60 * inch])
            t.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ]
                )
            )
            story.append(t)

    if data.experience:
        story += section_header_bold("Professional Experience", styles)
        for exp in data.experience:
            date_str = f"{exp.start} – {exp.end}" if exp.start else (exp.end or "")
            company_display = f" · {exp.company}" if exp.company else ""
            emp_display = f", {exp.emp_type}" if exp.emp_type else ""

            role_para = Paragraph(
                f"{exp.role}"
                f"<font color='#3a3a3a' size='9'>{company_display}</font>"
                f"<font color='#888888' size='9'>{emp_display}</font>",
                styles["role"],
            )
            header_row = [
                role_para,
                Paragraph(
                    date_str,
                    ParagraphStyle(
                        "bold_date",
                        parent=styles["company_meta"],
                        alignment=TA_RIGHT,
                        fontSize=9.5,
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
                story.append(
                    Paragraph(f"• {_apply_bold(b, bold_pattern)}", styles["bullet"])
                )

    if data.projects:
        story += section_header_bold("Projects", styles)
        for proj in data.projects:
            story.append(Paragraph(proj.title, styles["role"]))
            if proj.tech:
                story.append(Paragraph(f"Tech: {proj.tech}", styles["proj_tech"]))
            for b in proj.bullets:
                story.append(
                    Paragraph(f"• {_apply_bold(b, bold_pattern)}", styles["bullet"])
                )
            story.append(Spacer(1, 3))

    if data.achievements:
        story += section_header_bold("Achievements & Certifications", styles)
        for ach in data.achievements:
            story.append(
                Paragraph(f"• {_apply_bold(ach, bold_pattern)}", styles["bullet"])
            )

    if data.publications:
        story += section_header_bold("Publications", styles)
        for pub in data.publications:
            line = pub.title
            if pub.publisher:
                line += f" — {pub.publisher}"
            if pub.year:
                line += f" ({pub.year})"
            story.append(
                Paragraph(f"• {_apply_bold(line, bold_pattern)}", styles["pub"])
            )

    if data.education:
        story += section_header_bold("Education", styles)
        for edu in data.education:
            row = [
                Paragraph(f"<b>{edu.degree}</b>, {edu.institution}", styles["role"]),
                Paragraph(
                    edu.year or "",
                    ParagraphStyle(
                        "bold_edu_year",
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
