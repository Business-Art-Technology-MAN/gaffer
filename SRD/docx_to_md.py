"""Extract PCE_OTL_ProjectPlan_v2.docx -> PCE_OTL_ProjectPlan_v2.md (paragraphs + tables)."""
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

DOCX = Path(__file__).resolve().parent / "PCE_OTL_ProjectPlan_v2.docx"
OUT = Path(__file__).resolve().parent / "PCE_OTL_ProjectPlan_v2.md"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def paragraph_text(elem):
    parts = []
    for t in elem.findall(".//w:t", NS):
        if t.text:
            parts.append(t.text)
        if t.tail:
            parts.append(t.tail)
    return "".join(parts).strip()


def paragraph_style(p):
    ppr = p.find("w:pPr", NS)
    if ppr is None:
        return None
    ps = ppr.find("w:pStyle", NS)
    if ps is None:
        return None
    return ps.get(f"{{{NS['w']}}}val")


def format_paragraph(p):
    text = paragraph_text(p)
    if not text:
        return None
    style = paragraph_style(p)
    if style and "Heading" in style:
        try:
            level = int(style.replace("Heading", "").strip() or "1")
        except ValueError:
            level = 1
        level = min(max(level, 1), 6)
        return "#" * level + " " + text
    if style in ("Title", "Subtitle"):
        return "# " + text
    if style == "ListParagraph" or re.match(r"^([•\-\*]|[0-9]+\))\s+", text):
        if not text.startswith(("- ", "* ", "1.")):
            return "- " + text.lstrip("•*- ").strip()
    return text


def table_to_markdown(tbl):
    rows = []
    for tr in tbl.findall("w:tr", NS):
        cells = []
        for tc in tr.findall("w:tc", NS):
            cell_parts = []
            for p in tc.findall("w:p", NS):
                t = paragraph_text(p)
                if t:
                    cell_parts.append(t)
            cells.append(" ".join(cell_parts).replace("|", "\\|"))
        if any(cells):
            rows.append(cells)
    if not rows:
        return None
    width = max(len(r) for r in rows)
    norm = [r + [""] * (width - len(r)) for r in rows]

    if width == 1:
        if len(norm) == 1:
            return f"> {norm[0][0]}"
        return "\n".join(f"> {r[0]}" for r in norm if r[0])

    if width == 2 and len(norm) == 1:
        a, b = norm[0]
        if b:
            return f"**{a}** · *{b}*\n"
        return f"**{a}**\n"

    def is_sep_row(r):
        return all(re.match(r"^[\s\-–—:]+$", c) or c == "" for c in r)

    norm = [r for r in norm if not is_sep_row(r)]
    if len(norm) < 2:
        if len(norm) == 1 and width == 2:
            a, b = norm[0]
            if b:
                return f"**{a}** · *{b}*\n"
        return None

    header = norm[0]
    sep = ["---"] * width
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for r in norm[1:]:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


def body_elements(root):
    body = root.find("w:body", NS)
    if body is None:
        return []
    out = []
    for child in body:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        out.append((tag, child))
    return out


def main():
    with zipfile.ZipFile(DOCX) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    blocks = []

    for tag, el in body_elements(root):
        if tag == "p":
            line = format_paragraph(el)
            if line:
                blocks.append(line)
        elif tag == "tbl":
            md = table_to_markdown(el)
            if md:
                blocks.append(md)
        elif tag == "sectPr":
            continue

    text = "\n\n".join(blocks) + "\n"
    if text.lstrip().startswith("#"):
        pass
    else:
        first_nl = text.find("\n")
        if first_nl == -1:
            text = "# " + text.rstrip() + "\n"
        else:
            text = "# " + text[:first_nl].strip() + text[first_nl:]
    OUT.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT} ({len(blocks)} blocks)")


if __name__ == "__main__":
    main()
