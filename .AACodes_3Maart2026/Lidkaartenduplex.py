# -*- coding: utf-8 -*-
import os
from pathlib import Path
import math
import importlib
from datetime import datetime

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas

from excel_loader import load_members, load_back_dates
from layout_engine import build_layout, page_xy, scale_and_center
# =================== BASISPAD ===================
BASE_DIR = Path(__file__).resolve().parent
print("BASE_DIR =", BASE_DIR)

# =========================================================
# Koppel aan hoofdscript (ENIGE bron van waarheid)
# =========================================================
MODULE_NAME = "Lidkaart_2026_2027"
LK = importlib.import_module(MODULE_NAME)
print("✅ Duplex gebruikt hoofdscript:", LK.__file__)

MM = LK.MM
A4_W, A4_H = LK.A4_W, LK.A4_H

CARD_W = LK.CARD_W      # 85 mm
CARD_H = LK.CARD_H      # 54 mm

GRID_COLS = 2
GRID_ROWS = 5

PAGE_MARGIN = 18        # boven/onder
BACK_IMPOSE_X_SHIFT = LK.BACK_IMPOSE_X_SHIFT

SEASON_START_YEAR = LK.SEASON_START_YEAR
card_svg = LK.card_svg
back_card_svg = LK.back_card_svg
QR_URL = LK.QR_URL

# =========================================================
# ✅ MIDDENRUIMTE = 1 CM
# =========================================================
GAP_X = 0 * MM   # 1 cm exact

# Debug: teken kader rond elk kaartvak (handig om te meten)
DEBUG_FRAMES = False

# =========================================================
def main():
    # Excel inlezen
    xlsx_path = BASE_DIR / "leden.xlsx"
    members = load_members(xlsx_path)
    manual_dates = load_back_dates(xlsx_path)

    # Mappen
    svg_dir = BASE_DIR / "kaartjes_svg"
    svg_dir.mkdir(exist_ok=True)

    # FRONT SVG’s maken
    svg_files_front = []
    for m in members:
        code13 = m["code13"]
        full_name = m["name"]
        qr_url = m.get("qr") or QR_URL
        svg = card_svg(code13, full_name, qr_payload=qr_url)
        fp = svg_dir / f"{full_name.replace(' ', '_')}_{code13}.svg"
        fp.write_text(svg, encoding="utf-8")
        svg_files_front.append(fp)

    if not svg_files_front:
        print("❌ Geen leden om te printen.")
        return

    # BACK SVG (1 template)
    back_svg_path = svg_dir / f"kaartje_BACK_{SEASON_START_YEAR}_{SEASON_START_YEAR+1}.svg"
    back_svg_path.write_text(
        back_card_svg(SEASON_START_YEAR, manual_dates),
        encoding="utf-8"
    )

    # =================== POSITIES (A4) ===================
    gap_y = 0

    usable_h = A4_H - 2 * PAGE_MARGIN
    need_h = GRID_ROWS * CARD_H
    if need_h > usable_h:
        print("❌ Past niet in de hoogte: verlaag GRID_ROWS of PAGE_MARGIN.")
        return

    total_w = 2 * CARD_W + GAP_X
    x0 = (A4_W - total_w) / 2   # centreer horizontaal

    per_page = GRID_COLS * GRID_ROWS
    num_pages = math.ceil(len(svg_files_front) / per_page)

    out_duplex = BASE_DIR / (
    f"Lidkaartjes_A4_DUPLEX_GAP{int(round(GAP_X/MM))}mm_{SEASON_START_YEAR}-{SEASON_START_YEAR+1}_"
    f"{datetime.now():%Y%m%d_%H%M%S}.pdf"
)




    c = canvas.Canvas(str(out_duplex), pagesize=(A4_W, A4_H))

    # =================== Meet sizes 1x ===================
    # Front size
    d0 = svg2rlg(str(svg_files_front[0]))
    w0_front, h0_front = d0.width, d0.height

    # Back size
    b0 = svg2rlg(str(back_svg_path))
    w0_back, h0_back = b0.width, b0.height

    # Schalen + centreer offsets (1x)
    s_front = min(CARD_W / w0_front, CARD_H / h0_front, 1.0)
    dx_front = (CARD_W - w0_front * s_front) / 2
    dy_front = (CARD_H - h0_front * s_front) / 2

    s_back = min(CARD_W / w0_back, CARD_H / h0_back, 1.0)
    dx_back = (CARD_W - w0_back * s_back) / 2
    dy_back = (CARD_H - h0_back * s_back) / 2

    for p in range(num_pages):
        items = svg_files_front[p * per_page : (p + 1) * per_page]
        if not items:
            break

        # ================= FRONT PAGE =================
        for i, svg_path in enumerate(items):
            col = i % GRID_COLS
            row = i // GRID_COLS

            x_left = x0 + col * (CARD_W + GAP_X)
            y_bot  = A4_H - PAGE_MARGIN - (row + 1) * CARD_H 

            d = svg2rlg(str(svg_path))
            d.scale(s_front, s_front)

            if DEBUG_FRAMES:
                c.rect(x_left, y_bot, CARD_W, CARD_H)

            renderPDF.draw(d, c, x_left + dx_front, y_bot + dy_front)

        c.showPage()

        # ================= BACK PAGE =================
        c.saveState()
        c.translate(BACK_IMPOSE_X_SHIFT, 0)

        for i in range(per_page):
            col = i % GRID_COLS
            row = i // GRID_COLS

            x_left = x0 + col * (CARD_W + GAP_X)
            y_bot  = A4_H - PAGE_MARGIN - (row + 1) * CARD_H - row * gap_y

            db = svg2rlg(str(back_svg_path))
            db.scale(s_back, s_back)

            if DEBUG_FRAMES:
                c.rect(x_left, y_bot, CARD_W, CARD_H)

            renderPDF.draw(db, c, x_left + dx_back, y_bot + dy_back)

        c.restoreState()
        c.showPage()

    c.save()
    print(f"✅ DUPLEX A4-PDF aangemaakt: {out_duplex}")
    print("👉 Print duplex, 'flip on long edge'.")
    os.startfile(out_duplex)


if __name__ == "__main__":
    main()