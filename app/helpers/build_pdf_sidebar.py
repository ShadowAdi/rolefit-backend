"""
build_pdf_sidebar.py  —  "Sidebar" two-column template builder
───────────────────────────────────────────────────────────────
Architecture:
  The entire page is ONE outer Table with 2 columns:
    col[0]  = sidebar cell  (slate bg painted via a SidebarBackground Flowable)
    col[1]  = main cell     (white, normal content)

  Because ReportLab Tables don't paint cell backgrounds that extend to page
  edges cleanly at 0-margin, we use a full-bleed approach:
    • leftMargin = 0, rightMargin = 0, topMargin = 0, bottomMargin = 0
    • A single outer Table covers the full page width
    • Left cell has BACKGROUND TableStyle set to SB_BG
    • Inner padding added via LEFTPADDING / RIGHTPADDING / TOPPADDING

  Sidebar content: name, title, contact, skills, education
  Main content:    summary, experience, projects, achievements, publications
"""

import io
import re
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from .build_pdf import _format_header_links, _render_project_links
from app.utils.style.build_styles_sidebar import (
    build_styles_sidebar,
    _apply_bold,
    SB_BG,
    SB_TEAL,
    SB_RULE,
    SB_TEXT,
    MAIN_RULE,
    MAIN_ACCENT,
)

# ── Sidebar section label helper ──────────────────────────────────────────


def _sb_section(text: str, styles: dict) -> list:
    """Teal ALL-CAPS label + thin teal rule below for sidebar sections."""
    items = []
    items.append(Spacer(1, 8))
    items.append(
        HRFlowable(
            width="100%",
            thickness=0.4,
            color=SB_RULE,
            spaceBefore=0,
            spaceAfter=3,
        )
    )
    items.append(Paragraph(text.upper(), styles["sb_section"]))
    return items


def _main_section(text: str, styles: dict) -> list:
    """Dark uppercase label + thin rule below for main column sections."""
    items = []
    items.append(Paragraph(text.upper(), styles["main_section"]))
    items.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=MAIN_RULE,
            spaceBefore=1,
            spaceAfter=4,
        )
    )
    return items


# ── PDF Builder ───────────────────────────────────────────────────────────


def build_pdf_sidebar(data, bold_pattern: re.Pattern = None) -> bytes:
    buff = io.BytesIO()
    PW, PH = letter  # 612 x 792 pts
    SIDE_W = 2.20 * inch  # sidebar width
    MAIN_W = PW - SIDE_W  # main column width
    V_PAD = 0.40 * inch  # top/bottom page padding
    SB_PAD_H = 0.20 * inch  # sidebar inner horizontal padding
    SB_PAD_T = 0.38 * inch  # sidebar inner top padding
    MN_PAD_H = 0.22 * inch  # main inner horizontal padding
    MN_PAD_T = 0.38 * inch  # main inner top padding

    if bold_pattern is None:
        bold_pattern = re.compile(r"(?!)")

    styles = build_styles_sidebar()

    # ── Build sidebar story ───────────────────────────────────────────────
    sb = []
    h = data.header

    sb.append(Paragraph(h.name, styles["sb_name"]))
    if h.title:
        sb.append(Paragraph(h.title, styles["sb_title"]))

    # Contact
    sb += _sb_section("Contact", styles)
    contact_lines = []
    for field in [h.email, h.phone, h.location]:
        if field:
            contact_lines.append(field.replace("&", "&amp;"))
    if h.links:
        link_str = _format_header_links(h.links, accent_hex="#64ffda")
        if link_str:
            contact_lines.append(link_str)
    for line in contact_lines:
        sb.append(Paragraph(line, styles["sb_contact"]))

    # Skills
    if data.skills:
        sb += _sb_section("Skills", styles)
        for grp in data.skills:
            if not grp.items:
                continue
            sb.append(Paragraph(grp.category + ":", styles["sb_skill_cat"]))
            sb.append(Paragraph(", ".join(grp.items), styles["sb_skill_items"]))
            sb.append(Spacer(1, 3))

    # Education in sidebar
    if data.education:
        sb += _sb_section("Education", styles)
        for edu in data.education:
            sb.append(Paragraph(edu.degree, styles["sb_edu_degree"]))
            sb.append(Paragraph(edu.institution, styles["sb_edu_inst"]))
            if edu.year:
                sb.append(Paragraph(edu.year, styles["sb_edu_year"]))
            sb.append(Spacer(1, 4))

    # ── Build main story ──────────────────────────────────────────────────
    mn = []

    if data.summary:
        mn += _main_section("Summary", styles)
        mn.append(Paragraph(_apply_bold(data.summary, bold_pattern), styles["summary"]))

    if data.experience:
        mn += _main_section("Professional Experience", styles)
        for exp in data.experience:
            date_str = f"{exp.start} – {exp.end}" if exp.start else (exp.end or "")
            company_display = f" · {exp.company}" if exp.company else ""
            emp_display = f", {exp.emp_type}" if exp.emp_type else ""

            role_para = Paragraph(
                f"{exp.role}"
                f"<font color='#3a3a3a' size='8.5'>{company_display}</font>"
                f"<font color='#888888' size='8.5'>{emp_display}</font>",
                styles["role"],
            )
            header_row = [
                role_para,
                Paragraph(
                    date_str,
                    ParagraphStyle(
                        "sb_date",
                        parent=styles["company_meta"],
                        alignment=TA_RIGHT,
                        fontSize=8,
                    ),
                ),
            ]
            # Column widths must fit inside MAIN_W minus inner padding
            avail = MAIN_W - 2 * MN_PAD_H
            t = Table([header_row], colWidths=[avail * 0.62, avail * 0.38])
            t.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            mn.append(t)
            for b in exp.bullets:
                mn.append(
                    Paragraph(f"• {_apply_bold(b, bold_pattern)}", styles["bullet"])
                )
            mn.append(Spacer(1, 3))

    if data.projects:
        mn += _main_section("Projects", styles)
        for proj in data.projects:
            mn.append(Paragraph(proj.title, styles["role"]))
            link_para = _render_project_links(proj.links, styles["company_meta"])
            avail = MAIN_W - 2 * MN_PAD_H
            if proj.tech and link_para:
                row = [
                    Paragraph(f"Tech: {proj.tech}", styles["proj_tech"]),
                    link_para,
                ]
                t = Table([row], colWidths=[avail * 0.62, avail * 0.38])
                t.setStyle(
                    TableStyle(
                        [
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ]
                    )
                )
                mn.append(t)
            elif proj.tech:
                mn.append(Paragraph(f"Tech: {proj.tech}", styles["proj_tech"]))
            elif link_para:
                mn.append(link_para)
            for b in proj.bullets:
                mn.append(
                    Paragraph(f"• {_apply_bold(b, bold_pattern)}", styles["bullet"])
                )
            mn.append(Spacer(1, 3))

    if data.achievements:
        mn += _main_section("Achievements & Certifications", styles)
        for ach in data.achievements:
            mn.append(
                Paragraph(f"• {_apply_bold(ach, bold_pattern)}", styles["bullet"])
            )

    if data.publications:
        mn += _main_section("Publications", styles)
        for pub in data.publications:
            line = pub.title
            if pub.publisher:
                line += f" — {pub.publisher}"
            if pub.year:
                line += f" ({pub.year})"
            mn.append(Paragraph(f"• {_apply_bold(line, bold_pattern)}", styles["pub"]))

    # ── Assemble as a 2-column Table ──────────────────────────────────────
    # Each cell's content is wrapped in an inner Table to apply padding
    def _padded(story_items, pad_h, pad_t):
        """Wrap a list of flowables in a single-cell table for padding."""
        t = Table([[story_items]], colWidths=[None])
        t.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), pad_h),
                    ("RIGHTPADDING", (0, 0), (-1, -1), pad_h),
                    ("TOPPADDING", (0, 0), (-1, -1), pad_t),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), V_PAD),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        return t

    # ReportLab doesn't allow list of flowables directly in a Table cell;
    # we must use a nested Table (single col) as the container.
    sb_cell = _padded(sb, SB_PAD_H, SB_PAD_T)
    mn_cell = _padded(mn, MN_PAD_H, MN_PAD_T)

    outer = Table(
        [[sb_cell, mn_cell]],
        colWidths=[SIDE_W, MAIN_W],
    )
    outer.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), SB_BG),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    # Full-bleed doc — zero margins, outer table fills entire page
    doc = SimpleDocTemplate(
        buff,
        pagesize=letter,
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=0,
    )
    doc.build([outer])
    buff.seek(0)
    return buff.read()
