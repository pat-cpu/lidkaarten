# -*- coding: utf-8 -*-
from pathlib import Path
import re
import math
import unicodedata
import tempfile
from datetime import datetime

import pandas as pd

# =========================
# CONFIG (CENTRAAL)
# =========================
from config import EXCEL_PATH, SHEET, CODE_COL, NAME_COL

BASE_DIR = Path(__file__).resolve().parent

SORT_BY = "first"          # "first" of "last"
INCLUDE_NAME = True        # True = met naam

# 7 x 3 per blad
COLS = 3
ROWS = 7

TILE_MARGIN = 20
PAGE_MARGIN = 20
PAPER_SIZE = "A4"

OUT_BARCODES_DIR = BASE_DIR / "gegenereerde_barcodes"
OUT_BARCODES_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# HULPFUNCTIES
# =========================
def compute_checksum_from12(d12: str) -> int:
    s_odd = sum(int(d12[i]) for i in range(0, 12, 2))
    s_even = sum(int(d12[i]) for i in range(1, 12, 2))
    total = s_odd + 3 * s_even
    return (10 - (total % 10)) % 10

def normalize_ean13(c: str) -> str:
    c = re.sub(r"\.0$", "", str(c).strip())
    c = re.sub(r"\s+", "", c)

    if len(c) == 12 and c.isdigit():
        return c + str(compute_checksum_from12(c))
    if len(c) == 13 and c.isdigit():
        d12 = c[:12]
        return d12 + str(compute_checksum_from12(d12))
    return c

def norm_key(s: str) -> str:
    s2 = unicodedata.normalize("NFKD", str(s))
    s2 = "".join(ch for ch in s2 if not unicodedata.combining(ch))
    return s2.lower()

def split_name(name_raw: str):
    name_raw = re.sub(r"\s+", " ", (name_raw or "").strip())
    if not name_raw:
        return "", ""
    if " " in name_raw:
        return name_raw.split(" ", 1)
    return name_raw, ""

# =========================
# EAN13 TABLES
# =========================
A = {'0':'0001101','1':'0011001','2':'0010011','3':'0111101','4':'0100011','5':'0110001','6':'0101111','7':'0111011','8':'0110111','9':'0001011'}
B = {'0':'0100111','1':'0110011','2':'0011011','3':'0100001','4':'0011101','5':'0111001','6':'0000101','7':'0010001','8':'0001001','9':'0010111'}
C = {'0':'1110010','1':'1100110','2':'1101100','3':'1000010','4':'1011100','5':'1001110','6':'1010000','7':'1000100','8':'1001000','9':'1110100'}
parities = {0:"AAAAAA",1:"AABABB",2:"AABBAB",3:"AABBBA",4:"ABAABB",5:"ABBAAB",6:"ABBBAA",7:"ABABAB",8:"ABABBA",9:"ABBABA"}

def encode_bits(code13: str) -> str:
    first = int(code13[0])
    left = code13[1:7]
    right = code13[7:13]
    bits = "101"
    parity = parities[first]
    for i, d in enumerate(left):
        bits += A[d] if parity[i] == "A" else B[d]
    bits += "01010"
    for d in right:
        bits += C[d]
    bits += "101"
    return bits

def bits_to_svg(code13: str, name: str, module=2, bar_height=70, text_space=20):
    bits = encode_bits(code13)
    total_width = len(bits) * module + 20
    total_height = bar_height + text_space + 20

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{total_height}">',
        '<rect width="100%" height="100%" fill="white"/>'
    ]

    for i, b in enumerate(bits):
        if b == "1":
            y = 5
            h = bar_height
            if i < 3 or (45 <= i < 50) or i >= len(bits)-3:
                y = 0
                h = bar_height + 8
            parts.append(
                f'<rect x="{10 + i*module}" y="{y}" width="{module}" height="{h}" fill="black"/>'
            )

    parts.append(
        f'<text x="{total_width/2}" y="{bar_height+text_space-2}" '
        f'text-anchor="middle" font-family="Arial" font-size="12">{code13}</text>'
    )

    parts.append(
    f'<text x="{total_width/2}" y="{total_height-4}" '
    f'text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold">{name}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts), total_width, total_height

# =========================
# EXCEL INLEZEN
# =========================
print("Excel inlezen…")

df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET, dtype=str)
df.columns = [str(c).strip().replace("\ufeff", "") for c in df.columns]

entries = []
for _, row in df.iterrows():
    code_raw = row.get(CODE_COL)
    name_raw = row.get(NAME_COL)

    if pd.isna(code_raw) or pd.isna(name_raw):
        continue

    code13 = normalize_ean13(code_raw)
    if not (len(code13) == 13 and code13.isdigit()):
        continue

    first, last = split_name(name_raw)
    entries.append((code13, first, last))

print(f"{len(entries)} leden ingelezen.")

if SORT_BY == "last":
    entries = sorted(entries, key=lambda x: (norm_key(x[2]), norm_key(x[1])))
else:
    entries = sorted(entries, key=lambda x: norm_key(x[1]))

# =========================
# PAGINA INSTELLINGEN
# =========================
per_page = COLS * ROWS

if PAPER_SIZE.upper() == "LETTER":
    page_width, page_height = 612, 792
else:
    page_width, page_height = 595, 842

usable_w = page_width - 2 * PAGE_MARGIN
usable_h = page_height - 2 * PAGE_MARGIN
tile_w = usable_w / COLS
tile_h = usable_h / ROWS

# =========================
# SVG GENEREREN
# =========================
print("Barcodes renderen…")
tmp_barcodes = []

for code13, first, last in entries:
    label_name = f"{first} {last}".strip() if INCLUDE_NAME else ""
    svg, bw, bh = bits_to_svg(code13, label_name)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
    tmp.write(svg.encode("utf-8"))
    tmp.close()

    tmp_barcodes.append((Path(tmp.name), bw, bh))

# =========================
# PAGINA'S MAKEN (AUTO SCALE)
# =========================
print("Pagina’s bouwen…")
page_files = []

for page_idx in range(math.ceil(len(tmp_barcodes)/per_page)):
    items = tmp_barcodes[page_idx*per_page : (page_idx+1)*per_page]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_width}" height="{page_height}" '
        f'viewBox="0 0 {page_width} {page_height}">',
        '<rect width="100%" height="100%" fill="white"/>'
    ]

    for i, (barcode_path, bw, bh) in enumerate(items):
        col = i % COLS
        row = i // COLS

        x0 = PAGE_MARGIN + col * tile_w
        y0 = PAGE_MARGIN + row * tile_h

        avail_w = tile_w - 2 * TILE_MARGIN
        avail_h = tile_h - 2 * TILE_MARGIN

        scale = min(avail_w / bw, avail_h / bh) * 0.92

        dx = x0 + TILE_MARGIN + (avail_w - bw * scale) / 2
        dy = y0 + TILE_MARGIN + (avail_h - bh * scale) / 2

        inner = re.sub(
            r'(?s)^.*?<svg[^>]*>(.*)</svg>.*$',
            r'\1',
            barcode_path.read_text(encoding="utf-8")
        )

        parts.append(
            f'<g transform="translate({dx:.2f},{dy:.2f}) scale({scale:.4f})">{inner}</g>'
        )

    parts.append("</svg>")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
    tmp.write("\n".join(parts).encode("utf-8"))
    tmp.close()
    page_files.append(Path(tmp.name))

# =========================
# PDF MAKEN
# =========================
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from PyPDF2 import PdfMerger

print("PDF opbouwen…")

pdf_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
pdf_out = OUT_BARCODES_DIR / f"Barcode_met_naam_{pdf_stamp}.pdf"

tmp_pdfs = []

for svg_page in page_files:
    t = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    drawing = svg2rlg(str(svg_page))
    renderPDF.drawToFile(drawing, t.name)
    t.close()
    tmp_pdfs.append(Path(t.name))

merger = PdfMerger(strict=False)
for t in tmp_pdfs:
    merger.append(str(t))

with open(pdf_out, "wb") as f:
    merger.write(f)
merger.close()

print(f"PDF aangemaakt: {pdf_out}")

# OPRUIMEN
for t in tmp_pdfs:
    t.unlink(missing_ok=True)

for p in page_files:
    p.unlink(missing_ok=True)

for b, _, _ in tmp_barcodes:
    b.unlink(missing_ok=True)

print("Klaar.")