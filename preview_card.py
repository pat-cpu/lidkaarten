# -*- coding: utf-8 -*-
"""
preview_card.py
- Live preview van 1 kaart (front + back) zonder Excel
- # Gebruikt 1 bron van waarheid: lidkaart_.py
"""

import os
import copy
import importlib
from pathlib import Path
from datetime import datetime

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from tempfile import NamedTemporaryFile

MODULE_NAME = "lidkaart_layout"
LK = importlib.import_module(MODULE_NAME)

# --- 1 bron van waarheid ---
MM = LK.MM
A4_W, A4_H = LK.A4_W, LK.A4_H
CARD_W, CARD_H = LK.CARD_W, LK.CARD_H
PAGE_MARGIN = getattr(LK, "PAGE_MARGIN_MM", 6.0) * MM
BACK_IMPOSE_X_SHIFT = getattr(LK, "BACK_IMPOSE_X_SHIFT", 0.0)

SEASON_START_YEAR = LK.SEASON_START_YEAR
card_svg = LK.card_svg
back_card_svg = LK.back_card_svg
QR_URL = getattr(LK, "QR_URL", None)

BASE_DIR = Path(__file__).resolve().parent


def _svg_to_drawing(svg_text: str):
    with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
        tmp.write(svg_text)
        tmp.flush()
        d = svg2rlg(tmp.name)
    try:
        os.unlink(tmp.name)
    except Exception:
        pass
    return d


def _scale_and_center(w0: float, h0: float):
    s = min(CARD_W / w0, CARD_H / h0)
    s = min(s, 1.0)  # nooit vergroten
    dx = (CARD_W - w0 * s) / 2.0
    dy = (CARD_H - h0 * s) / 2.0
    return s, dx, dy


def main():
    # ✅ herlaad LK elke run (zodat je wijziging meteen zichtbaar is)
    global LK, card_svg, back_card_svg, SEASON_START_YEAR
    LK = importlib.reload(LK)
    card_svg = LK.card_svg
    back_card_svg = LK.back_card_svg
    SEASON_START_YEAR = LK.SEASON_START_YEAR

    # TESTDATA (pas aan als je wil)
    test_code13 = "2000000000002"
    test_name = "PREVIEW - Patrick"
    qr = QR_URL or "https://kaartclub-the-whiskies.webnode.be/"

    svg_front = card_svg(test_code13, test_name, qr_payload=qr)
    svg_back = back_card_svg(SEASON_START_YEAR, manual_dates=None)

    d_front = _svg_to_drawing(svg_front)
    d_back0 = _svg_to_drawing(svg_back)

    s_f, dx_f, dy_f = _scale_and_center(d_front.width, d_front.height)
    s_b, dx_b, dy_b = _scale_and_center(d_back0.width, d_back0.height)

    out_pdf = BASE_DIR / f"PREVIEW_{SEASON_START_YEAR}-{SEASON_START_YEAR+1}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    c = canvas.Canvas(str(out_pdf), pagesize=(A4_W, A4_H))

    # Positie: linksboven (zoals positie 1)
    x_left = (A4_W - (2 * CARD_W)) / 2.0  # gecentreerd alsof 2 kolommen
    y_bot = A4_H - PAGE_MARGIN - CARD_H  # bovenmarge

    # FRONT
    d_front.scale(s_f, s_f)
    renderPDF.draw(d_front, c, x_left + dx_f, y_bot + dy_f)
    c.showPage()

    # BACK (met shift)
    c.saveState()
    c.translate(BACK_IMPOSE_X_SHIFT, 0)
    d_back = copy.deepcopy(d_back0)
    d_back.scale(s_b, s_b)
    renderPDF.draw(d_back, c, x_left + dx_b, y_bot + dy_b)
    c.restoreState()
    c.showPage()

    c.save()
    print("✅ Preview PDF:", out_pdf)
    try:
        os.startfile(out_pdf)
    except Exception:
        pass


if __name__ == "__main__":
    main()