import io
import re
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from .build_pdf import _format_header_links
from app.utils.style.build_styles_minimalist import (
    build_styles_minimalist,
    section_header_minimalist,
    _apply_bold,
)


def build_pdf_minimalist(data, minimal_pattern: re.Pattern = None) -> bytes:
    buff = io.BytesIO()
    M = 0.55 * inch

    if minimal_pattern is None:
        minimal_pattern = re.compile(r"(?!)")  # Pattern that matches nothing

    doc = SimpleDocTemplate(
        buff, pagesize=letter, leftMargin=M, rightMargin=M, topMargin=0.50 * inch
    )

    styles = build_styles_minimalist()
    story = []

    h = data.header

    story.append(Paragraph(h.name, styles["name"]))
    if h.title:
        story.append(Paragraph(h.title, styles["title"]))

    contact_parts = []
    for field in [h.email, h.phone, h.location]:
        if field:
            contact_parts.append(field.replace("&", "&amp;"))

    if h.links:
        link_str = _format_header_links(h.links, accent_hex="#2d2d2d")
        if link_str:
            contact_parts.append(link_str)

    if contact_parts:
        story.append(Paragraph("  ·  ".join(contact_parts), styles["contact"]))

    if data.summary:
        story += section_header_minimalist("Summary", styles)
        story.append(
            Paragraph(_apply_bold(data.summary, minimal_pattern), styles["summary"])
        )

    if data.skills:
        story += section_header_minimalist("Skills & Technologies", styles)
        for grp in data.skills:
            if not grp.items:
                continue
            row = [
                Paragraph(grp.category + ":", styles["skill_category"]),
                Paragraph(", ".join(grp.items), styles["skill_items"]),
            ]
            t = Table([row], colWidths=[1.70 * inch, 5.55 * inch])
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
        story += section_header_minimalist("Professional Experience", styles)
        for exp in data.experience:
            date_str = f"{exp.start} – {exp.end}" if exp.start else (exp.end or "")
            company_display = f" · {exp.company}" if exp.company else ""
            emp_display = f", {exp.emp_type}" if exp.emp_type else ""

            role_para = Paragraph(
                f"{exp.role}"
                f"<font color='#4a4a4a' size='9'>{company_display}</font>"
                f"<font color='#888888' size='9'>{emp_display}</font>",
                styles["role"],
            )

            header_row = [
                role_para,
                Paragraph(
                    date_str,
                    ParagraphStyle(
                        "mini_date",
                        parent=styles["company_meta"],
                        alignment=TA_RIGHT,
                        fontSize=9,
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
                    Paragraph(f"• {_apply_bold(b, minimal_pattern)}", styles["bullet"])
                )

    if data.projects:
        story += section_header_minimalist("Projects", styles)
        for proj in data.projects:
            story.append(Paragraph(proj.title, styles["role"]))
            if proj.tech:
                story.append(Paragraph(f"Tech: {proj.tech}", styles["proj_tech"]))
            for b in proj.bullets:
                story.append(
                    Paragraph(f"• {_apply_bold(b, minimal_pattern)}", styles["bullet"])
                )
            story.append(Spacer(1, 4))

    if data.achievements:
        story += section_header_minimalist("Achievements & Certifications", styles)
        for ach in data.achievements:
            story.append(
                Paragraph(f"• {_apply_bold(ach, minimal_pattern)}", styles["bullet"])
            )

    if data.publications:
        story += section_header_minimalist("Publications", styles)
        for pub in data.publications:
            line = pub.title
            if pub.publisher:
                line += f" — {pub.publisher}"
            if pub.year:
                line += f" ({pub.year})"
            story.append(
                Paragraph(f"• {_apply_bold(line, minimal_pattern)}", styles["pub"])
            )

    if data.education:
        story += section_header_minimalist("Education", styles)
        for edu in data.education:
            row = [
                Paragraph(f"<b>{edu.degree}</b>, {edu.institution}", styles["role"]),
                Paragraph(
                    edu.year or "",
                    ParagraphStyle(
                        "mini_edu_year",
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
