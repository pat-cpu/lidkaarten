# -*- coding: utf-8 -*-
"""
print_single_card.py
- Print 1 lidkaart (front + back) op A4
- Front op pagina 1, back op pagina 2
- Front wordt gekalibreerd via:
    LK.FRONT_PRINT_SHIFT_X / LK.FRONT_PRINT_SHIFT_Y
- Back blijft ongewijzigd
"""

from __future__ import annotations

import os
import sys
import copy
import importlib
from pathlib import Path
from datetime import datetime
from tempfile import NamedTemporaryFile

import pandas as pd
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas

from excel_loader import load_members_df, load_back_dates
from config import EXCEL_PATH, CODE_COL, NAME_COL

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

BACK_IMPOSE_X_SHIFT = getattr(LK, "BACK_IMPOSE_X_SHIFT", 0.0)

FRONT_PRINT_SHIFT_X = getattr(LK, "FRONT_PRINT_SHIFT_X", 0.0)
FRONT_PRINT_SHIFT_Y = getattr(LK, "FRONT_PRINT_SHIFT_Y", 0.0)

SEASON_START_YEAR = LK.SEASON_START_YEAR
card_svg = LK.card_svg
back_card_svg = LK.back_card_svg
QR_URL = getattr(LK, "QR_URL", None)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def _page_xy(col: int, row: int, shift_x: float = 0.0, shift_y: float = 0.0) -> tuple[float, float]:
    total_w = COLS * CARD_W + (COLS - 1) * GAP_X
    x0 = (A4_W - total_w) / 2.0
    y_top = A4_H - PAGE_MARGIN

    x_left = x0 + col * (CARD_W + GAP_X) + shift_x
    y_bot = y_top - (row + 1) * CARD_H - row * GAP_Y + shift_y
    return x_left, y_bot


def _scale_and_center(w0: float, h0: float) -> tuple[float, float, float]:
    s = min(CARD_W / w0, CARD_H / h0)
    if SCALE_MAX_1:
        s = min(s, 1.0)
    dx = (CARD_W - w0 * s) / 2.0
    dy = (CARD_H - h0 * s) / 2.0
    return s, dx, dy


def _pos_to_col_row(pos_1_10: int) -> tuple[int, int]:
    if not 1 <= pos_1_10 <= (COLS * ROWS):
        raise ValueError(f"pos moet 1..{COLS*ROWS} zijn")
    i = pos_1_10 - 1
    col = i % COLS
    row = i // COLS
    return col, row


def _svg_to_drawing(svg_text: str):
    with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
        tmp.write(svg_text)
        tmp.flush()
        drawing = svg2rlg(tmp.name)
    try:
        os.unlink(tmp.name)
    except Exception:
        pass
    return drawing


def _find_member_by_name(df: pd.DataFrame, name: str):
    name_l = name.strip().lower()
    hit = df[df[NAME_COL].astype(str).str.strip().str.lower() == name_l]
    return None if hit.empty else hit.iloc[0]


def generate_single_card(pos_front: int, name: str, pos_back: int | None = None):
    """
    Maak 1 PDF met 2 pagina's:
    - pagina 1: front
    - pagina 2: back

    Standaard:
    1 -> 2
    2 -> 1
    3 -> 4
    4 -> 3
    enz.
    """
    name = (name or "").strip()
    if not name:
        print("❌ Geen naam ingegeven.")
        return

    if pos_back is None:
        if pos_front % 2 == 1:
            pos_back = pos_front + 1
        else:
            pos_back = pos_front - 1

    try:
        col_f, row_f = _pos_to_col_row(pos_front)
        col_b, row_b = _pos_to_col_row(pos_back)
    except ValueError as e:
        print(f"❌ {e}")
        return

    df = load_members_df()
    if df is None or df.empty:
        print("❌ Geen leden gevonden in Excel.")
        return

    row0 = _find_member_by_name(df, name)
    if row0 is None:
        print(f"❌ Lid niet gevonden: {name}")
        return

    code13 = str(row0[CODE_COL]).strip()
    full_name = str(row0[NAME_COL]).strip()

    qr_url = None
    if "qr" in df.columns:
        try:
            qr_url = str(row0.get("qr") or "").strip() or None
        except Exception:
            qr_url = None
    qr_url = qr_url or QR_URL

    xlsx_path = Path(EXCEL_PATH)
    manual_dates = load_back_dates(xlsx_path) if xlsx_path.exists() else None
    if manual_dates and manual_dates[0].year != SEASON_START_YEAR:
        manual_dates = None

    svg_front = card_svg(code13, full_name, qr_payload=qr_url)
    svg_back = back_card_svg(SEASON_START_YEAR, manual_dates)

    d_front0 = _svg_to_drawing(svg_front)
    d_back0 = _svg_to_drawing(svg_back)

    s_f, dx_f, dy_f = _scale_and_center(d_front0.width, d_front0.height)
    s_b, dx_b, dy_b = _scale_and_center(d_back0.width, d_back0.height)

    x_f, y_f = _page_xy(col_f, row_f, FRONT_PRINT_SHIFT_X, FRONT_PRINT_SHIFT_Y)
    x_b, y_b = _page_xy(col_b, row_b)

    out_pdf = OUTPUT_DIR / (
        f"single_card_{full_name.replace(' ', '_')}_"
        f"F{pos_front}_B{pos_back}_"
        f"{SEASON_START_YEAR}-{SEASON_START_YEAR+1}_"
        f"{datetime.now():%Y%m%d_%H%M%S}.pdf"
    )

    c = canvas.Canvas(str(out_pdf), pagesize=(A4_W, A4_H))

    # FRONT
    d_front = copy.deepcopy(d_front0)
    d_front.scale(s_f, s_f)

    if DEBUG_FRAMES:
        c.rect(x_f, y_f, CARD_W, CARD_H)

    renderPDF.draw(d_front, c, x_f + dx_f, y_f + dy_f)
    c.showPage()

    # BACK
    c.saveState()
    c.translate(BACK_IMPOSE_X_SHIFT, 0)

    d_back = copy.deepcopy(d_back0)
    d_back.scale(s_b, s_b)

    if DEBUG_FRAMES:
        c.rect(x_b, y_b, CARD_W, CARD_H)

    renderPDF.draw(d_back, c, x_b + dx_b, y_b + dy_b)

    c.restoreState()
    c.showPage()

    c.save()

    print(f"✅ Single kaart PDF: {out_pdf}")
    try:
        os.startfile(out_pdf)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        pos_front = int(input(f"Front positie (1–{COLS*ROWS}): ").strip())
    except Exception:
        print("❌ Ongeldige front positie.")
        sys.exit(1)

    name = input("Naam: ").strip()
    generate_single_card(pos_front=pos_front, name=name)