# -*- coding: utf-8 -*-
"""
Lidkaartenduplex.py
- Print alle lidkaarten duplex in één PDF
- Front pagina's + back pagina's per blad
- Back wordt per rij links/rechts gespiegeld:
    1 <-> 2
    3 <-> 4
    5 <-> 6
    7 <-> 8
    9 <-> 10
- Front kan gekalibreerd worden via:
    LK.FRONT_PRINT_SHIFT_X / LK.FRONT_PRINT_SHIFT_Y
- Back gebruikt:
    LK.BACK_IMPOSE_X_SHIFT
"""

from __future__ import annotations

import os
import math
import copy
import importlib
from pathlib import Path
from datetime import datetime
from tempfile import NamedTemporaryFile

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas

from config import EXCEL_PATH, CODE_COL, NAME_COL
from excel_loader import load_members_df, load_back_dates

# ============================================================
# ENIGE BRON VAN WAARHEID
# ============================================================
MODULE_NAME = "lidkaart_layout"
LK = importlib.import_module(MODULE_NAME)

MM = LK.MM
A4_W, A4_H = LK.A4_W, LK.A4_H
CARD_W, CARD_H = LK.CARD_W, LK.CARD_H

COLS = getattr(LK, "PRINT_COLS", 2)
ROWS = getattr(LK, "PRINT_ROWS", 5)

PAGE_MARGIN = getattr(LK, "PAGE_MARGIN_MM", 6.0) * MM
GAP_X = getattr(LK, "GAP_X_MM", 0.0) * MM
GAP_Y = getattr(LK, "GAP_Y_MM", 0.0) * MM

SCALE_MAX_1 = getattr(LK, "SCALE_MAX_1", True)
DEBUG_FRAMES = getattr(LK, "DEBUG_FRAMES", False)

FRONT_PRINT_SHIFT_X = getattr(LK, "FRONT_PRINT_SHIFT_X", 0.0)
FRONT_PRINT_SHIFT_Y = getattr(LK, "FRONT_PRINT_SHIFT_Y", 0.0)

BACK_IMPOSE_X_SHIFT = getattr(LK, "BACK_IMPOSE_X_SHIFT", 0.0)

SEASON_START_YEAR = LK.SEASON_START_YEAR
card_svg = LK.card_svg
back_card_svg = LK.back_card_svg

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# HELPERS
# ============================================================
def page_xy(col: int, row: int, shift_x: float = 0.0, shift_y: float = 0.0) -> tuple[float, float]:
    """
    Linksonder van een kaartvak op A4.
    """
    total_w = COLS * CARD_W + (COLS - 1) * GAP_X
    x0 = (A4_W - total_w) / 2.0
    y_top = A4_H - PAGE_MARGIN

    x_left = x0 + col * (CARD_W + GAP_X) + shift_x
    y_bot = y_top - (row + 1) * CARD_H - row * GAP_Y + shift_y
    return x_left, y_bot


def scale_and_center(w0: float, h0: float) -> tuple[float, float, float]:
    s = min(CARD_W / w0, CARD_H / h0)
    if SCALE_MAX_1:
        s = min(s, 1.0)
    dx = (CARD_W - w0 * s) / 2.0
    dy = (CARD_H - h0 * s) / 2.0
    return s, dx, dy


def svg_to_drawing(svg_text: str):
    with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
        tmp.write(svg_text)
        tmp.flush()
        drawing = svg2rlg(tmp.name)
    try:
        os.unlink(tmp.name)
    except Exception:
        pass
    return drawing


def mirror_col_for_back(col: int) -> int:
    """
    Spiegel links/rechts voor backside bij 2 kolommen:
    0 -> 1
    1 -> 0
    """
    if COLS != 2:
        # fallback: als ooit ander aantal kolommen gebruikt wordt,
        # gewoon dezelfde kolom behouden
        return col
    return 1 - col


# ============================================================
# MAIN
# ============================================================
def generate_duplex_pdf():
    df = load_members_df()
    if df is None or df.empty:
        print("❌ Geen leden gevonden in Excel.")
        return

    entries = [(str(r[CODE_COL]).strip(), str(r[NAME_COL]).strip()) for _, r in df.iterrows()]
    if not entries:
        print("❌ Geen leden in leden.xlsx.")
        return

    per_page = COLS * ROWS
    num_pages = math.ceil(len(entries) / per_page)

    # BACK datums
    xlsx_path = Path(EXCEL_PATH)
    manual_dates = load_back_dates(xlsx_path) if xlsx_path.exists() else None
    if manual_dates and manual_dates[0].year != SEASON_START_YEAR:
        manual_dates = None

    back_svg_text = back_card_svg(SEASON_START_YEAR, manual_dates)

    out_pdf = OUTPUT_DIR / (
        f"Lidkaarten_DUPLEX_{SEASON_START_YEAR}-{SEASON_START_YEAR+1}_"
        f"{datetime.now():%Y%m%d_%H%M%S}.pdf"
    )
    print(f"📄 Duplex PDF maken: {out_pdf}")

    c = canvas.Canvas(str(out_pdf), pagesize=(A4_W, A4_H))

    # Eén keer meten front
    sample_front_svg = card_svg(entries[0][0], entries[0][1])
    d_front0 = svg_to_drawing(sample_front_svg)
    s_f, dx_f, dy_f = scale_and_center(d_front0.width, d_front0.height)

    # Eén keer meten back
    d_back0 = svg_to_drawing(back_svg_text)
    s_b, dx_b, dy_b = scale_and_center(d_back0.width, d_back0.height)

    for p in range(num_pages):
        batch = entries[p * per_page : (p + 1) * per_page]

        # ================= FRONT PAGE =================
        for i, (code13, name) in enumerate(batch):
            col = i % COLS
            row = i // COLS

            x_left, y_bot = page_xy(col, row, FRONT_PRINT_SHIFT_X, FRONT_PRINT_SHIFT_Y)

            svg_text = card_svg(code13, name)
            drawing = svg_to_drawing(svg_text)
            drawing.scale(s_f, s_f)

            if DEBUG_FRAMES:
                c.rect(x_left, y_bot, CARD_W, CARD_H)

            renderPDF.draw(drawing, c, x_left + dx_f, y_bot + dy_f)

        c.showPage()

        # ================= BACK PAGE =================
        c.saveState()
        c.translate(BACK_IMPOSE_X_SHIFT, 0)

        # Back-template is voor iedereen identiek
        for i in range(len(batch)):
            col = i % COLS
            row = i // COLS

            col_back = mirror_col_for_back(col)
            x_left, y_bot = page_xy(col_back, row)

            drawing = copy.deepcopy(d_back0)
            drawing.scale(s_b, s_b)

            if DEBUG_FRAMES:
                c.rect(x_left, y_bot, CARD_W, CARD_H)

            renderPDF.draw(drawing, c, x_left + dx_b, y_bot + dy_b)

        c.restoreState()
        c.showPage()

    c.save()

    print("✔ Duplex PDF klaar.")
    try:
        os.startfile(out_pdf)
    except Exception:
        pass


if __name__ == "__main__":
    generate_duplex_pdf()