# -*- coding: utf-8 -*-
from pathlib import Path
import importlib
from tempfile import NamedTemporaryFile

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas

# =========================================================
# Koppel aan hoofdscript (ENIGE bron van waarheid)
# =========================================================
MODULE_NAME = "Lidkaart_2026_2027"
LK = importlib.import_module(MODULE_NAME)

BASE_DIR = Path(__file__).resolve().parent

# Layout + seizoen uit LK
MM = LK.MM
A4_W, A4_H = LK.A4_W, LK.A4_H
GRID_COLS, GRID_ROWS = LK.GRID_COLS, LK.GRID_ROWS
PAGE_MARGIN, CELL_MARGIN = LK.PAGE_MARGIN, LK.CELL_MARGIN
BACK_IMPOSE_X_SHIFT = LK.BACK_IMPOSE_X_SHIFT
SEASON_START_YEAR = LK.SEASON_START_YEAR

card_svg = LK.card_svg
back_card_svg = LK.back_card_svg

# =========================================================
# ✅ Snijvriendelijke tussenruimte tussen de 2 kolommen
# (mm → points)
# =========================================================
INNER_GAP = 2 * MM  # start: 2 mm (zet bv. 1*MM .. 4*MM naar smaak)


def generate_single_card(code13: str, full_name: str, qr_payload=None, pos_front: int = 1, pos_back: int = 1):
    """
    Genereert een 2-pagina PDF:
    - pagina 1: front op positie pos_front (1..10)
    - pagina 2: back op positie pos_back (1..10) met BACK_IMPOSE_X_SHIFT
    """
    out_pdf = BASE_DIR / f"single_card_{full_name.replace(' ', '_')}_{SEASON_START_YEAR}-{SEASON_START_YEAR+1}.pdf"
    c = canvas.Canvas(str(out_pdf), pagesize=(A4_W, A4_H))

    # SVG's maken via LK
    svg_front = card_svg(code13, full_name, qr_payload=qr_payload)
    svg_back = back_card_svg(SEASON_START_YEAR, manual_dates=None)

    def draw(svg_text: str, position: int, shift_x: float = 0.0):
        if position < 1 or position > (GRID_COLS * GRID_ROWS):
            raise ValueError(f"Pos moet tussen 1 en {GRID_COLS * GRID_ROWS} liggen.")

        # cell_w gebruikt een echte INNER_GAP tussen kolommen
        cell_w = (A4_W - 2 * PAGE_MARGIN - INNER_GAP) / GRID_COLS
        cell_h = (A4_H - 2 * PAGE_MARGIN) / GRID_ROWS

        idx = position - 1
        col = idx % GRID_COLS
        row = idx // GRID_COLS

        with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
            tmp.write(svg_text)
            tmp.flush()
            drawing = svg2rlg(tmp.name)

        w0, h0 = drawing.width, drawing.height

        # ✅ NOOIT VERGROTEN: max 1.0
        s = min(
            (cell_w - 2 * CELL_MARGIN) / w0,
            (cell_h - 2 * CELL_MARGIN) / h0,
            1.0
        )

        # ✅ x_left gebruikt (cell_w + INNER_GAP) zodat gap echt zichtbaar wordt
        x_left = PAGE_MARGIN + col * (cell_w + INNER_GAP) + (cell_w - w0 * s) / 2 + shift_x
        y_bot  = A4_H - (PAGE_MARGIN + (row + 1) * cell_h) + (cell_h - h0 * s) / 2

        drawing.scale(s, s)
        renderPDF.draw(drawing, c, x_left, y_bot)

    # --- FRONT PAGE ---
    draw(svg_front, pos_front, shift_x=0.0)
    c.showPage()

    # --- BACK PAGE ---
    # shift_x = BACK_IMPOSE_X_SHIFT (duplex fine-tuning)
    draw(svg_back, pos_back, shift_x=BACK_IMPOSE_X_SHIFT)
    c.showPage()

    c.save()
    return out_pdf


# Handig voor snelle test
if __name__ == "__main__":
    # Voorbeeldtest (pas aan naar een echte code/naam)
    pdf = generate_single_card("2092600000012", "Test Persoon", qr_payload=None, pos_front=1, pos_back=1)
    print("✅ PDF gemaakt:", pdf)