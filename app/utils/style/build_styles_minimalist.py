import io
import re
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    Flowable,
)
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.colors import HexColor
from app.core.resume_colors import MINI_BLACK, MINI_ACCENT, MINI_SUBTEXT, MINI_RULE
from app.helpers.build_pdf import _format_header_links

DARK_GRAY = HexColor("#4a4a4a")
TECH_COLOR = HexColor("#777777")


def build_styles_minimalist() -> dict:
    base = getSampleStyleSheet()

    def s(name, **kw) -> ParagraphStyle:
        defaults = dict(
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=MINI_BLACK,
            spaceAfter=0,
            spaceBefore=0,
        )
        defaults.update(kw)
        return ParagraphStyle(name=name, parent=base["Normal"], **defaults)

    return {
        "name": s(
            "mini_name",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=MINI_ACCENT,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "title": s(
            "mini_title",
            fontSize=11,
            textColor=MINI_SUBTEXT,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "contact": s(
            "mini_contact",
            fontSize=8.5,
            leading=11,
            textColor=MINI_SUBTEXT,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "role": s(
            "mini_role",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=MINI_BLACK,
        ),
        "company_meta": s(
            "mini_company_meta",
            fontSize=8.5,
            leading=11,
            textColor=MINI_SUBTEXT,
            spaceAfter=1,
        ),
        "bullet": s(
            "mini_bullet",
            fontSize=9.5,
            leading=13,
            leftIndent=10,
            firstLineIndent=-10,
            spaceAfter=1,
        ),
        "skill_category": s(
            "mini_skill_cat",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=MINI_SUBTEXT,
        ),
        "skill_items": s("mini_skill_items", fontSize=8.5, leading=12),
        "summary": s("mini_summary", fontSize=9.5, leading=13, spaceAfter=4),
        "pub": s("mini_pub", fontSize=9, leading=12, spaceAfter=1),
        "edu_desc": s(
            "mini_edu_desc", fontSize=9, leading=11, textColor=DARK_GRAY, spaceAfter=1
        ),
        "proj_tech": s(
            "mini_proj_tech",
            fontSize=8.5,
            leading=11,
            textColor=TECH_COLOR,
            fontName="Helvetica-Oblique",
            spaceAfter=2,
        ),
    }


class MiniSectionHeader(Flowable):
    FONT = "Helvetica"
    FONT_SIZE = 8.5
    RULE_T = 0.4
    SPACE_BEFORE = 12
    SPACE_AFTER = 5

    def __init__(self,text:str):
        super().__init__()
        self.text()=text.upper()
        self._height=self.SPACE_BEFORE+self.FONT_SIZE+self.SPACE_AFTER
    
    def wrap(self,aw,ah):
        self._width=aw
        return aw, self._height

    def draw(self):
        c=self.canv
        rule_y=self.SPACE_AFTER + self.FONT_SIZE + 3
        c.setStrokeColor(MINI_RULE)
        c.setLineWidth(self.RULE_T)
        c.line(0,rule_y,self._width,rule_y)
        text_y=self.SPACE_AFTER
        c.setFont(self.FONT, self.FONT_SIZE)
        c.setFillColor(MINI_SUBTEXT)
        c.drawString(0, text_y, self.text)
        c.setFont(self.FONT, self.FONT_SIZE)
        c.setFillColor(MINI_SUBTEXT)
        c.drawString(0, text_y, self.text)
 
    
def section_header_minimalist(text:str,styles:dict)->list:
    return MiniSectionHeader(text=text)


_BASE_BOLD = re.compile(
    r"\b("
    r"\d[\d,\.]*\s*%|"
    r"\d[\d,\.]*\+?\s*(?:users|ms|seconds?|minutes?|hours?|days?|months?|requests?|"
    r"records?|events?|transactions?|calls?|endpoints?|services?|nodes?|instances?)|"
    r"Built|Engineered|Developed|Designed|Implemented|Optimized|Reduced|Increased|"
    r"Improved|Automated|Shipped|Led|Architected|Deployed|Migrated|Integrated|"
    r"Launched|Scaled|Delivered|Established|Created|Streamlined|"
    r"REST(?:ful)?|GraphQL|gRPC|Microservices?|CI/CD|Docker|Kubernetes|AWS|GCP|Azure|"
    r"PostgreSQL|MongoDB|Redis|Kafka|RabbitMQ|Elasticsearch|TypeORM|Prisma|"
    r"React|Next\.js|NestJS|Node\.js|FastAPI|Django|Spring Boot|Express|"
    r"TypeScript|JavaScript|Python|Go|Golang|Rust|Java|C\+\+|"
    r"LLM|GPT|ML|AI|NLP|RAG|fine.tun(?:ing|ed)"
    r")\b",
    re.IGNORECASE,
)

def _apply_bold(text:str,pattern:re.Pattern)->str:
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return pattern.sub(lambda m: f"<b>{m.group(0)}</b>", safe)


def build_pdf_minimalist(data,bold_pattern:re.Pattern)->bytes:
    buff=io.BytesIO()
    M=0.55*inch
    
    doc=SimpleDocTemplate(
        buff,
        pagesize=letter,
        leftMargin=M,
        rightMargin=M,
        topMargin=0.50*inch
    )
    
    styles=build_styles_minimalist()
    story=[]
    
    h=data.header

    story.append(Paragraph(h.name,styles["name"]))
    if h.title:
        story.append(Paragraph(h.title,styles["title"]))
    
    contact_parts=[]
    for field in [h.email,h.phone,h.location]:
        if field:
            contact_parts.append(field.replace("&","&amp;"))
    
    if h.links:
        link_str=_format_header_links(h.links,accent_hex="#2d2d2d")
        if link_str:
            contact_parts.append(link_str)
    
    if contact_parts:
        story.append(Paragraph("  ·  ".join(contact_parts), styles["contact"]))
    
    if data.summary:
        story+=section_header_minimalist("Summary",styles)
        story.append(Paragraph(_apply_bold(data.summary,bold_pattern),styles["summary"]))
    
    if data.skills:
        story+=section_header_minimalist("Skills & Technologies",styles)
        for grp in data.skills:
            if not grp.items:
                continue
            row = [
                Paragraph(grp.category + ":", styles["skill_category"]),
                Paragraph(", ".join(grp.items), styles["skill_items"]),
            ]
            t=Table([row],colWidths=[1.70*inch,5.55*inch])
            t.setStyle(TableStyle([
                ("VALIGN",        (0,0), (-1,-1), "TOP"),
                ("BOTTOMPADDING", (0,0), (-1,-1), 3),
                ("TOPPADDING",    (0,0), (-1,-1), 2),
            ]))
            story.append(t)
    
    if data.experience:
        story+=section_header_minimalist("Professional Experience",styles)
        for exp in data.experience:
            date_str = f"{exp.start} – {exp.end}" if exp.start else (exp.end or "")
            company_display = f" · {exp.company}" if exp.company else ""
            emp_display     = f", {exp.emp_type}" if exp.emp_type else ""
            
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
                    ParagraphStyle("mini_date", parent=styles["company_meta"],
                                   alignment=TA_RIGHT, fontSize=9),
                ),
            ]
            t = Table([header_row], colWidths=[4.5 * inch, 3.0 * inch])
            
            t.setStyle(TableStyle([
                ("VALIGN",        (0,0), (-1,-1), "TOP"),
                ("BOTTOMPADDING", (0,0), (-1,-1), 1),
            ]))
            
            story.append(t)
            for b in exp.bullets:
                story.append(Paragraph(f"• {_apply_bold(b, bold_pattern)}", styles["bullet"]))
    
    if data.projects:
        story += section_header_minimalist("Projects", styles)
        for proj in data.projects:
            story.append(Paragraph(proj.title, styles["role"]))
            if proj.tech:
                story.append(Paragraph(f"Tech: {proj.tech}", styles["proj_tech"]))
            for b in proj.bullets:
                story.append(Paragraph(f"• {_apply_bold(b, bold_pattern)}", styles["bullet"]))
            story.append(Spacer(1, 4))
    
    if data.achievments:
        story += section_header_minimalist("Achievements & Certifications", styles)
        for ach in data.achievements:
            story.append(Paragraph(f"• {_apply_bold(ach, bold_pattern)}", styles["bullet"]))
    
    if data.publications:
        story += section_header_minimalist("Publications", styles)
        for pub in data.publications:
            line = pub.title
            if pub.publisher:
                line += f" — {pub.publisher}"
            if pub.year:
                line += f" ({pub.year})"
            story.append(Paragraph(f"• {_apply_bold(line, bold_pattern)}", styles["pub"]))
    
    if data.education:
        story+=section_header_minimalist("Education",styles)
        for edu in data.education:
            row=[
                Paragraph(f"<b>{edu.degree}</b>, {edu.institution}", styles["role"]),
                Paragraph(
                    edu.year or "",
                    ParagraphStyle("mini_edu_year", parent=styles["company_meta"],
                                   alignment=TA_RIGHT, fontSize=9),
                ),
            ]
            t=Table([row],colWidths=[5.5*inch,2.0*inch])
            t.setStyle(
                TableStyle([
                ("VALIGN",        (0,0), (-1,-1), "TOP"),
                ("BOTTOMPADDING", (0,0), (-1,-1), 2),
                ])
            )
            story.append(t)
            if edu.location:
                story.append(Paragraph(edu.location, styles["company_meta"]))
            if hasattr(edu, "description") and edu.description:
                safe = edu.description.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                story.append(Paragraph(safe, styles["edu_desc"]))
    
    
    doc.build(story)
    buff.seek(0)
    return buff.read()
