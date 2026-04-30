"""
build_pdf_bold.py  —  "Bold / Accent-bar" template builder
────────────────────────────────────────────────────────────
Key structural difference from Classic:
  • Header is a TWO-COLUMN Table: name (left, large) | title + contact (right, small)
  • Section labels have a red-pink left accent bar + thin rule below
  • Skill category labels are red-pink coloured
  • topMargin slightly larger (0.45in) — cleaner breathing room at top
"""

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
from .build_pdf import _format_header_links, _render_project_links
from app.utils.style.build_styles_bold import (
    build_styles_bold,
    section_header_bold,
    _apply_bold,
    BOLD_ACCENT,
)


def build_pdf_bold(data, bold_pattern: re.Pattern = None) -> bytes:
    buff = io.BytesIO()
    M = 0.50 * inch

    if bold_pattern is None:
        bold_pattern = re.compile(r"(?!)")

    doc = SimpleDocTemplate(
        buff,
        pagesize=letter,
        leftMargin=M,
        rightMargin=M,
        topMargin=0.45 * inch,
        bottomMargin=0.40 * inch,
    )

    styles = build_styles_bold()
    story = []

    # ── Header: name LEFT | title + contact RIGHT ─────────────────────────
    h = data.header

    contact_parts = []
    for field in [h.email, h.phone, h.location]:
        if field:
            contact_parts.append(field.replace("&", "&amp;"))
    if h.links:
        link_str = _format_header_links(h.links, accent_hex="#e8445a")
        if link_str:
            contact_parts.append(link_str)

    right_col = []
    if h.title:
        right_col.append(Paragraph(h.title, styles["title"]))
    if contact_parts:
        right_col.append(Paragraph(" | ".join(contact_parts), styles["contact"]))

    # Pad right column with spacer if only one line
    if len(right_col) == 1:
        right_col.insert(0, Spacer(1, 14))

    from reportlab.platypus import KeepTogether

    header_table = Table(
        [[Paragraph(h.name, styles["name"]), right_col]],
        colWidths=[3.8 * inch, 3.7 * inch],
    )
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(header_table)

    # Thin divider under header
    from reportlab.platypus import HRFlowable

    story.append(Spacer(1, 6))
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=BOLD_ACCENT,
            spaceAfter=4,
            spaceBefore=0,
        )
    )

    # ── Summary ───────────────────────────────────────────────────────────
    if data.summary:
        story += section_header_bold("Summary", styles)
        story.append(
            Paragraph(_apply_bold(data.summary, bold_pattern), styles["summary"])
        )

    # ── Skills ────────────────────────────────────────────────────────────
    if data.skills:
        story += section_header_bold("Skills & Technologies", styles)
        for grp in data.skills:
            if not grp.items:
                continue
            row = [
                Paragraph(grp.category + ":", styles["skill_category"]),
                Paragraph(", ".join(grp.items), styles["skill_items"]),
            ]
            t = Table([row], colWidths=[1.75 * inch, 5.55 * inch])
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

    # ── Experience ────────────────────────────────────────────────────────
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
                    Paragraph(f"• {_apply_bold(b, bold_pattern)}", styles["bullet"])
                )

    # ── Projects ──────────────────────────────────────────────────────────
    if data.projects:
        story += section_header_bold("Projects", styles)
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
                story.append(
                    Paragraph(f"• {_apply_bold(b, bold_pattern)}", styles["bullet"])
                )
            story.append(Spacer(1, 3))

    # ── Achievements ──────────────────────────────────────────────────────
    if data.achievements:
        story += section_header_bold("Achievements & Certifications", styles)
        for ach in data.achievements:
            story.append(
                Paragraph(f"• {_apply_bold(ach, bold_pattern)}", styles["bullet"])
            )

    # ── Publications ──────────────────────────────────────────────────────
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

    # ── Education ─────────────────────────────────────────────────────────
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
