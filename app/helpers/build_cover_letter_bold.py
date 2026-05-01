"""
build_cover_letter_pdf_bold.py  —  BOLD cover letter template
──────────────────────────────────────────────────────────────
Structural differences from Classic:
  • Full-width dark navy header block (BoldCLHeader Flowable) containing:
      - Name LEFT-aligned (white, 22pt)
      - Contact RIGHT-aligned (soft lavender, 8.5pt)
    Both rendered ON the dark background — no plain text above.
  • topMargin=0 so the header block bleeds to the top edge
  • Red-pink (1.5pt) accent rule replaces the classic thin gray HR
  • Company block has a 3pt left accent bar (drawn inline)
  • Sign-off text is red-pink accent colour
"""

import io
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    HRFlowable,
    Flowable,
)
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from app.schema.CoverLetterData import CoverLetterData
from app.utils.style.cl_styles_bold import _build_cl_styles_bold, BOLD_BG, BOLD_ACCENT


class BoldCLHeader(Flowable):
    """Full-width dark navy rectangle — name (left) + contact (right) in white/lavender."""

    PAD_V = 16
    PAD_H = 14

    def __init__(self, name: str, contact_markup: str, styles: dict):
        super().__init__()
        self.name_text = name
        self.contact_text = contact_markup
        self.styles = styles

    def wrap(self, aw, ah):
        self._width = aw
        inner_w = aw - 2 * self.PAD_H

        self._name_para = Paragraph(self.name_text, self.styles["name"])
        self._contact_para = Paragraph(self.contact_text, self.styles["contact"])

        _, nh = self._name_para.wrap(inner_w * 0.6, 9999)
        _, ch = self._contact_para.wrap(inner_w * 0.4, 9999)
        self._height = max(nh, ch) + self.PAD_V * 2
        return aw, self._height

    def draw(self):
        c = self.canv

        inner_w = self._width - 2 * self.PAD_H
        name_w = inner_w * 0.6
        contact_w = inner_w * 0.4

        _, nh = self._name_para.wrap(name_w, 9999)
        _, ch = self._contact_para.wrap(contact_w, 9999)

        name_y = (self._height - nh) / 2
        contact_y = (self._height - ch) / 2

        self._name_para.drawOn(c, self.PAD_H, name_y)
        self._contact_para.drawOn(c, self.PAD_H + name_w, contact_y)


class AccentLeftBar(Flowable):
    """3pt red-pink left bar beside the company/role block."""

    BAR_W = 3
    GAP = 8

    def __init__(self, markup: str, style: ParagraphStyle):
        super().__init__()
        self._markup = markup
        self._style = style

    def wrap(self, aw, ah):
        self._width = aw
        inner_w = aw - self.BAR_W - self.GAP
        self._para = Paragraph(self._markup, self._style)
        _, self._ph = self._para.wrap(inner_w, 9999)
        self._height = self._ph + 4
        return aw, self._height

    def draw(self):
        c = self.canv
        c.setFillColor(BOLD_ACCENT)
        c.rect(0, 0, self.BAR_W, self._height, fill=1, stroke=0)
        self._para.drawOn(c, self.BAR_W + self.GAP, 2)


def build_cover_letter_pdf_bold(data: CoverLetterData) -> bytes:
    buff = io.BytesIO()
    M = 0.80 * inch

    doc = SimpleDocTemplate(
        buff,
        pagesize=letter,
        leftMargin=M,
        rightMargin=M,
        topMargin=0.0 * inch,  # header block bleeds to top
        bottomMargin=0.55 * inch,
    )

    styles = _build_cl_styles_bold()
    story = []

    candidate = data.candidate
    company = data.company

    # ── Dark header block ──────────────────────────────────────────────
    contact_parts = []
    for field in [candidate.email, candidate.phone, candidate.location]:
        if field and field.strip():
            contact_parts.append(field.strip().replace("&", "&amp;"))
    if candidate.linkedin and candidate.linkedin.strip():
        url = candidate.linkedin.strip().replace("&", "&amp;")
        contact_parts.append(
            f'<link href="{url}"><font color="#c0c8f0">LinkedIn</font></link>'
        )
    contact_markup = " | ".join(contact_parts)

    story.append(BoldCLHeader(candidate.name or "", contact_markup, styles))
    story.append(Spacer(1, 10))

    # ── Red-pink accent rule ───────────────────────────────────────────
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=BOLD_ACCENT,
            spaceBefore=0,
            spaceAfter=10,
        )
    )

    # ── Date ──────────────────────────────────────────────────────────
    if data.date:
        story.append(Paragraph(data.date, styles["date"]))
        story.append(Spacer(1, 8))

    # ── Company block with left accent bar ────────────────────────────
    if company.name or company.role:
        lines = []
        if company.name:
            lines.append(f"<b>{company.name}</b>")
        if company.role:
            lines.append(f"Re: {company.role} Position")
        story.append(AccentLeftBar("<br/>".join(lines), styles["company_block"]))
        story.append(Spacer(1, 4))

    story.append(Paragraph("Dear Hiring Manager,", styles["salutation"]))

    for key in ("opening", "body1", "body2", "closing"):
        text = getattr(data.paragraphs, key, "").strip()
        if not text:
            continue
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(safe, styles["body"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph(data.sign_off + ",", styles["signoff"]))
    if candidate.name:
        story.append(Paragraph(candidate.name, styles["signed_name"]))

    doc.build(story)
    buff.seek(0)
    return buff.read()
