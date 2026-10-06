import re, glob, os, textwrap
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Preformatted,
                                Table, TableStyle, PageBreak, ListFlowable, ListItem, KeepTogether, HRFlowable)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "GitHub-Actions-Course.pdf")

ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=10.5, leading=15, spaceAfter=6)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=22, spaceAfter=10, textColor=colors.HexColor("#1f3a5f"))
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=16, spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#1f3a5f"))
h3 = ParagraphStyle("h3", parent=ss["Heading3"], fontSize=12.5, spaceBefore=10, spaceAfter=4)
code = ParagraphStyle("c", fontName="Courier", fontSize=8.2, leading=10.4, backColor=colors.HexColor("#f4f5f7"),
                      borderPadding=6, spaceBefore=4, spaceAfter=10, leftIndent=4)
cell = ParagraphStyle("cell", parent=body, fontSize=9, leading=12, spaceAfter=0)
quote = ParagraphStyle("q", parent=body, leftIndent=12, textColor=colors.HexColor("#555555"),
                       borderPadding=4, backColor=colors.HexColor("#eef4fb"))

def clean(t):
    return (t.replace("→", "->").replace("—", "-").replace("–", "-")
             .replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"'))

def inline(t):
    t = escape(clean(t))
    spans = []
    def stash(m):
        spans.append('<font name="Courier" size="9">%s</font>' % m.group(1))
        return "\x00%d\x00" % (len(spans) - 1)
    t = re.sub(r"`([^`]+)`", stash, t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\w)", r"<i>\1</i>", t)
    t = re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="blue">\1</link>', t)
    t = re.sub(r"(?<![\"=>])(https?://[^\s<)]+)", r'<link href="\1" color="blue">\1</link>', t)
    return t

def wrap_code(src, width=98):
    out = []
    for line in clean(src).rstrip("\n").split("\n"):
        if len(line) <= width:
            out.append(line)
        else:
            ind = len(line) - len(line.lstrip())
            out += textwrap.wrap(line, width, subsequent_indent=" " * (ind + 4), break_long_words=True)
    return "\n".join(out)

def code_block(src):
    return Preformatted(wrap_code(src), code)

def parse_md(md):
    lines = md.split("\n")
    story, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            story.append(code_block("\n".join(buf))); i += 1; continue
        if ln.startswith("# "):
            story.append(Paragraph(inline(ln[2:]), h1))
        elif ln.startswith("## "):
            story.append(Paragraph(inline(ln[3:]), h2))
        elif ln.startswith("### "):
            story.append(Paragraph(inline(ln[4:]), h3))
        elif ln.strip() == "---":
            story.append(HRFlowable(width="100%", color=colors.lightgrey, spaceBefore=6, spaceAfter=6))
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[\s\-|]+\|$", lines[i]):
                    rows.append([Paragraph(inline(c.strip()), cell) for c in lines[i].strip("|").split("|")])
                i += 1
            t = Table(rows, repeatRows=1, colWidths=[0.6*inch, 0.5*inch, 3.3*inch, 2.1*inch][:len(rows[0])] if len(rows[0]) == 4 else None)
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dde6f2")),
                                   ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            story += [t, Spacer(1, 8)]; continue
        elif re.match(r"^(\s*)([-*]|\d+\.) ", ln):
            items, ordered = [], bool(re.match(r"^\s*\d+\.", ln))
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.) ", lines[i]):
                txt = re.sub(r"^\s*([-*]|\d+\.) ", "", lines[i]).strip()
                i += 1
                sub = []
                while i < len(lines) and lines[i].startswith("   ") and lines[i].strip():
                    if lines[i].strip().startswith("```"):
                        i += 1; buf = []
                        while i < len(lines) and not lines[i].strip().startswith("```"):
                            buf.append(lines[i][3:]); i += 1
                        i += 1; sub.append(code_block("\n".join(buf)))
                    else:
                        txt += " " + lines[i].strip(); i += 1
                txt = txt.replace("[ ]", "[  ]")
                items.append(ListItem([Paragraph(inline(txt), body)] + sub))
            story.append(ListFlowable(items, bulletType="1" if ordered else "bullet",
                                      bulletFontSize=9, leftIndent=18))
            continue
        elif ln.startswith(">"):
            story.append(Paragraph(inline(ln.lstrip("> ")), quote))
        elif ln.strip():
            story.append(Paragraph(inline(ln), body))
        i += 1
    return story

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.grey)
    canvas.drawCentredString(letter[0] / 2, 0.45 * inch, f"GitHub Actions: Zero to Hero  -  page {doc.page}")
    canvas.restoreState()

story = parse_md(open(os.path.join(HERE, "README.md")).read())

story += [PageBreak(), Paragraph("Appendix: Example files", h1),
          Paragraph("Each file below is also in the <font name='Courier'>workflows/</font> and <font name='Courier'>app/</font> folders. "
                    "Copy workflows into <font name='Courier'>.github/workflows/</font> in your repo.", body)]
files = sorted(glob.glob(os.path.join(HERE, "workflows", "*.yml"))) + sorted(glob.glob(os.path.join(HERE, "app", "*")))
for f in files:
    rel = os.path.relpath(f, HERE)
    story.append(Paragraph(rel, h3))
    story.append(code_block(open(f).read()))

SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.8*inch, rightMargin=0.8*inch,
                  topMargin=0.8*inch, bottomMargin=0.8*inch,
                  title="GitHub Actions: Zero to Hero", author="Claude").build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
