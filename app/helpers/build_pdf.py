import io
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


def _render_project_links(
    links: list[str], base_style: ParagraphStyle
) -> Paragraph | None:
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

    h = data.header
    story.append(Paragraph(h.name, styles["name"]))
    if h.title:
        story.append(Paragraph(h.title, styles["title"]))

    contact_parts = [p for p in [h.email, h.phone, h.location] if p]
    contact_parts += h.links
    if contact_parts:
        safe_parts = [p.replace("&", "&amp;") for p in contact_parts]
        story.append(Paragraph(" | ".join(safe_parts), styles["contact"]))

    story.append(
        HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=3, spaceAfter=4)
    )

    if data.summary:
        story += section_header("Summary", styles)
        story.append(Paragraph(data.summary, styles["summary"]))
        story.append(Spacer(1, 2))

    if data.skills:
        story += section_header("Skills & Technologies", styles)
        for grp in data.skills:
            if not grp.items:
                continue
            row = [
                Paragraph(grp.category + ":", styles["skill_category"]),
                Paragraph(", ".join(grp.items), styles["skill_items"]),
            ]
            t = Table([row], colWidths=[1.45 * inch, 5.9 * inch])
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
            role_with_company = Paragraph(
                f"{exp.role}<font color='#888888' size='9'>{company_display}</font>",
                styles["role"],
            )

            header_row = [
                role_with_company,
                Paragraph(
                    date_str,
                    ParagraphStyle(
                        "date",
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
                story.append(bullet_para(b, styles))
            story.append(Spacer(1, 4))

    if data.projects:
        story += section_header("Projects", styles)
        for proj in data.projects:
            story.append(Paragraph(proj.title, styles["role"]))

            link_para = _render_project_links(proj.links, styles["company_meta"])
            if proj.tech and link_para:
                row = [
                    Paragraph(f"Tech: {proj.tech}", styles["company_meta"]),
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
                story.append(Paragraph(f"Tech: {proj.tech}", styles["company_meta"]))
            elif link_para:
                story.append(link_para)

            for b in proj.bullets:
                story.append(bullet_para(b, styles))
            story.append(Spacer(1, 3))  # was 4

    if data.achievements:
        story += section_header("Achievements & Certifications", styles)
        for ach in data.achievements:
            story.append(bullet_para(ach, styles))
        story.append(Spacer(1, 2))

    if data.publications:
        story += section_header("Publications", styles)
        for pub in data.publications:
            line = pub.title
            if pub.publisher:
                line += f" — {pub.publisher}"
            if pub.year:
                line += f" ({pub.year})"
            story.append(Paragraph(f"• {line}", styles["pub"]))
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
                story.append(Paragraph(edu.description, styles["edu_desc"]))

    doc.build(story)
    buff.seek(0)
    return buff.read()
