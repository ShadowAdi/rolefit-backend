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


def build_pdf_bold(data, bold_pattern: re.Pattern) -> bytes:
    buff = io.BytesIO()
    M = 0.48 * inch

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
        contact_markup = " | ".join(contact_parts)

    story.append(BoldHeaderBlock(h.name, h.title or "", contact_markup, styles))
    story.append(Spacer(1, 8))

    if data.summary:
        story += section_header_bold("Summary", styles)
        story.append(
            Paragraph(_apply_bold(data.summary, bold_pattern), styles["summary"])
        )
