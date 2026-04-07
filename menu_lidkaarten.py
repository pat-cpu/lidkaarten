<<<<<<< HEAD
# -*- coding: utf-8 -*-
import os
import sys
import math
import subprocess
import importlib
from pathlib import Path
from datetime import datetime
from tempfile import NamedTemporaryFile

import pandas as pd
from colorama import init, Fore
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas

from config import EXCEL_PATH, SHEET, CODE_COL, NAME_COL
from excel_loader import load_members_df, load_back_dates
from print_single_card import generate_single_card

import lidkaart_layout as LK
print("✅ menu gebruikt hoofdscript:", LK.__file__)

SEASON_START_YEAR = LK.SEASON_START_YEAR
card_svg = LK.card_svg
back_card_svg = LK.back_card_svg
print("✅ card_svg module:", card_svg.__module__)
print("✅ back_card_svg module:", back_card_svg.__module__)

init(autoreset=True)

BASE_DIR = Path(__file__).resolve().parent

MODULE_NAME = "lidkaart_layout"

LK = importlib.import_module(MODULE_NAME)

MM = LK.MM
A4_W, A4_H = LK.A4_W, LK.A4_H

CARD_W = LK.CARD_W
CARD_H = LK.CARD_H

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

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def page_xy(col: int, row: int, shift_x: float = 0.0, shift_y: float = 0.0) -> tuple[float, float]:
    total_w = COLS * CARD_W + (COLS - 1) * GAP_X
    x0 = (A4_W - total_w) / 2
    y_top = A4_H - PAGE_MARGIN

    x_left = x0 + col * (CARD_W + GAP_X) + shift_x
    y_bot = y_top - (row + 1) * CARD_H - row * GAP_Y + shift_y
    return x_left, y_bot


def scale_and_center(w0: float, h0: float) -> tuple[float, float, float]:
    s = min(CARD_W / w0, CARD_H / h0)
    if SCALE_MAX_1:
        s = min(s, 1.0)
    dx = (CARD_W - w0 * s) / 2
    dy = (CARD_H - h0 * s) / 2
    return s, dx, dy


def list_members():
    df = load_members_df()
    if df is None:
        return
    print(df[[CODE_COL, NAME_COL]].to_string(index=False))


def member_info():
    df = load_members_df()
    if df is None:
        return
    name = input("Naam: ").strip()
    hit = df[df[NAME_COL].astype(str).str.strip().str.lower() == name.strip().lower()]
    if hit.empty:
        print("❌ Niet gevonden.")
        return
    print(hit.to_string(index=False))


def generate_all_front():
    df = load_members_df()
    if df is None:
        return

    entries = [(str(r[CODE_COL]).strip(), str(r[NAME_COL]).strip()) for _, r in df.iterrows()]
    if not entries:
        print("❌ Geen leden in leden.xlsx.")
        return

    per_page = COLS * ROWS
    num_pages = math.ceil(len(entries) / per_page)

    out_pdf = OUTPUT_DIR / f"Lidkaarten_A4_FRONT_all_{SEASON_START_YEAR}-{SEASON_START_YEAR+1}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    print(f"📄 FRONT A4 bundel maken: {out_pdf}")

    c = canvas.Canvas(str(out_pdf), pagesize=(A4_W, A4_H))

    sample_svg = card_svg(entries[0][0], entries[0][1])
    with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
        tmp.write(sample_svg)
        tmp.flush()
        d0 = svg2rlg(tmp.name)
    w0, h0 = d0.width, d0.height
    s0, dx0, dy0 = scale_and_center(w0, h0)

    for p in range(num_pages):
        batch = entries[p * per_page : (p + 1) * per_page]
        for i, (code13, name) in enumerate(batch):
            col = i % COLS
            row = i // COLS

            x_left, y_bot = page_xy(col, row, FRONT_PRINT_SHIFT_X, FRONT_PRINT_SHIFT_Y)

            svg_text = card_svg(code13, name)
            with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
                tmp.write(svg_text)
                tmp.flush()
                drawing = svg2rlg(tmp.name)

            drawing.scale(s0, s0)

            if DEBUG_FRAMES:
                c.rect(x_left, y_bot, CARD_W, CARD_H)

            renderPDF.draw(drawing, c, x_left + dx0, y_bot + dy0)

        c.showPage()

    c.save()
    try:
        os.startfile(out_pdf)
    except Exception:
        pass
    print("✔ FRONT bundel klaar.\n")


def generate_all_back():
    df = load_members_df()
    if df is None:
        return

    entries = [(str(r[CODE_COL]).strip(), str(r[NAME_COL]).strip()) for _, r in df.iterrows()]
    if not entries:
        print("❌ Geen leden in leden.xlsx.")
        return

    xlsx_path = EXCEL_PATH
    manual_dates = load_back_dates(xlsx_path) if Path(xlsx_path).exists() else None
    if manual_dates and manual_dates[0].year != SEASON_START_YEAR:
        manual_dates = None

    back_svg_text = back_card_svg(SEASON_START_YEAR, manual_dates)

    per_page = COLS * ROWS
    num_pages = math.ceil(len(entries) / per_page)

    out_pdf = OUTPUT_DIR / f"Lidkaarten_A4_BACK_all_{SEASON_START_YEAR}-{SEASON_START_YEAR+1}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    print(f"📄 BACK A4 bundel maken: {out_pdf}")

    c = canvas.Canvas(str(out_pdf), pagesize=(A4_W, A4_H))

    with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
        tmp.write(back_svg_text)
        tmp.flush()
        b0 = svg2rlg(tmp.name)
    w0, h0 = b0.width, b0.height
    s0, dx0, dy0 = scale_and_center(w0, h0)

    for p in range(num_pages):
        c.saveState()
        c.translate(BACK_IMPOSE_X_SHIFT, 0)

        for i in range(per_page):
            col = i % COLS
            row = i // COLS
            x_left, y_bot = page_xy(col, row)

            with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
                tmp.write(back_svg_text)
                tmp.flush()
                drawing = svg2rlg(tmp.name)

            drawing.scale(s0, s0)

            if DEBUG_FRAMES:
                c.rect(x_left, y_bot, CARD_W, CARD_H)

            renderPDF.draw(drawing, c, x_left + dx0, y_bot + dy0)

        c.restoreState()
        c.showPage()

    c.save()
    try:
        os.startfile(out_pdf)
    except Exception:
        pass
    print("✔ BACK bundel klaar.\n")


def cleanup_outputs():
    patterns = ["*.pdf"]
    removed = 0
    for pat in patterns:
        for f in OUTPUT_DIR.glob(pat):
            try:
                f.unlink()
                removed += 1
            except Exception:
                pass
    print(f"🧹 Opruiming klaar: {removed} bestanden verwijderd.\n")


# def open_output_folders():
#     try:
#         os.startfile(str(OUTPUT_DIR))
#     except Exception:
#         pass


def testprint_four_cards():
    df = load_members_df()
    if df is None or df.empty:
        print("❌ Geen leden.")
        return

    entries = [(str(r[CODE_COL]).strip(), str(r[NAME_COL]).strip()) for _, r in df.head(4).iterrows()]
    if not entries:
        print("❌ Geen leden.")
        return

    out_pdf = OUTPUT_DIR / f"TEST_4cards_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    c = canvas.Canvas(str(out_pdf), pagesize=(A4_W, A4_H))

    sample_svg = card_svg(entries[0][0], entries[0][1])
    with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
        tmp.write(sample_svg)
        tmp.flush()
        d0 = svg2rlg(tmp.name)
    w0, h0 = d0.width, d0.height
    s0, dx0, dy0 = scale_and_center(w0, h0)

    for i, (code13, name) in enumerate(entries):
        col = i % COLS
        row = i // COLS
        x_left, y_bot = page_xy(col, row, FRONT_PRINT_SHIFT_X, FRONT_PRINT_SHIFT_Y)

        svg_text = card_svg(code13, name)
        with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
            tmp.write(svg_text)
            tmp.flush()
            drawing = svg2rlg(tmp.name)

        drawing.scale(s0, s0)
        if DEBUG_FRAMES:
            c.rect(x_left, y_bot, CARD_W, CARD_H)
        renderPDF.draw(drawing, c, x_left + dx0, y_bot + dy0)

    c.save()
    try:
        os.startfile(out_pdf)
    except Exception:
        pass
    print("✔ Testprint 4 kaarten klaar.\n")


def main():
    while True:
        print(
            f"""
==============================
THE WHISKIES - LIDKAARTEN MENU
Seizoen {SEASON_START_YEAR}-{SEASON_START_YEAR+1}
Layout: COLS={COLS} ROWS={ROWS} GAP_X={GAP_X/MM:.1f}mm GAP_Y={GAP_Y/MM:.1f}mm MARGIN={PAGE_MARGIN/MM:.1f}mm
==============================
1) Print 1 lidkaart (single, positie 1–10)
2) Print alle lidkaarten duplex (Lidkaartenduplex.py)
3) Ledenlijst tonen
4) Info over lid
5) Print alle FRONT lidkaarten (A4 bundel)
6) Print alle BACK lidkaarten (A4 bundel)
7) Output opruimen (PDF)
9) Live preview kaart (preview_card.py)
10) Testprint 4 kaarten
11) Nieuw lid toevoegen (nieuw_lid.py)
12) Afsluiten
"""
        )
        choice = input("> ").strip()

        if choice == "1":
            name = input("Naam: ").strip()
            try:
                pos = int(input("Positie (1–10): ").strip())
                if not 1 <= pos <= 10:
                    raise ValueError
            except ValueError:
                print("❌ Ongeldige positie (1–10).")
                continue
            generate_single_card(pos, name)

        elif choice == "2":
            subprocess.run([sys.executable, "Lidkaartenduplex.py"])

        elif choice == "3":
            list_members()

        elif choice == "4":
            member_info()

        elif choice == "5":
            generate_all_front()

        elif choice == "6":
            generate_all_back()

        elif choice == "7":
            cleanup_outputs()

        # elif choice == "8":
        #     open_output_folders()

        elif choice == "9":
           subprocess.run([sys.executable, "preview_card.py"])

        elif choice == "10":
            testprint_four_cards()

        elif choice == "11":
            subprocess.run([sys.executable, "nieuw_lid.py"])

        # elif choice == "12":
        #     subprocess.run([sys.executable, "menu_barcodes.py"])

        elif choice == "12":
            print("Programma afgesloten.")
            break
        else:
            print("❌ Ongeldige keuze.\n")


if __name__ == "__main__":
=======
# -*- coding: utf-8 -*-
import os
import sys
import math
import subprocess
import importlib
from pathlib import Path
from datetime import datetime
from tempfile import NamedTemporaryFile

import pandas as pd
from colorama import init, Fore
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas

from config import EXCEL_PATH, SHEET, CODE_COL, NAME_COL
from excel_loader import load_members_df, load_back_dates
from print_single_card import generate_single_card

import lidkaart_layout as LK
print("✅ menu gebruikt hoofdscript:", LK.__file__)

SEASON_START_YEAR = LK.SEASON_START_YEAR
card_svg = LK.card_svg
back_card_svg = LK.back_card_svg
print("✅ card_svg module:", card_svg.__module__)
print("✅ back_card_svg module:", back_card_svg.__module__)

init(autoreset=True)

BASE_DIR = Path(__file__).resolve().parent

MODULE_NAME = "lidkaart_layout"

LK = importlib.import_module(MODULE_NAME)

MM = LK.MM
A4_W, A4_H = LK.A4_W, LK.A4_H

CARD_W = LK.CARD_W
CARD_H = LK.CARD_H

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

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def page_xy(col: int, row: int, shift_x: float = 0.0, shift_y: float = 0.0) -> tuple[float, float]:
    total_w = COLS * CARD_W + (COLS - 1) * GAP_X
    x0 = (A4_W - total_w) / 2
    y_top = A4_H - PAGE_MARGIN

    x_left = x0 + col * (CARD_W + GAP_X) + shift_x
    y_bot = y_top - (row + 1) * CARD_H - row * GAP_Y + shift_y
    return x_left, y_bot


def scale_and_center(w0: float, h0: float) -> tuple[float, float, float]:
    s = min(CARD_W / w0, CARD_H / h0)
    if SCALE_MAX_1:
        s = min(s, 1.0)
    dx = (CARD_W - w0 * s) / 2
    dy = (CARD_H - h0 * s) / 2
    return s, dx, dy


def list_members():
    df = load_members_df()
    if df is None:
        return
    print(df[[CODE_COL, NAME_COL]].to_string(index=False))


def member_info():
    df = load_members_df()
    if df is None:
        return
    name = input("Naam: ").strip()
    hit = df[df[NAME_COL].astype(str).str.strip().str.lower() == name.strip().lower()]
    if hit.empty:
        print("❌ Niet gevonden.")
        return
    print(hit.to_string(index=False))


def generate_all_front():
    df = load_members_df()
    if df is None:
        return

    entries = [(str(r[CODE_COL]).strip(), str(r[NAME_COL]).strip()) for _, r in df.iterrows()]
    if not entries:
        print("❌ Geen leden in leden.xlsx.")
        return

    per_page = COLS * ROWS
    num_pages = math.ceil(len(entries) / per_page)

    out_pdf = OUTPUT_DIR / f"Lidkaarten_A4_FRONT_all_{SEASON_START_YEAR}-{SEASON_START_YEAR+1}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    print(f"📄 FRONT A4 bundel maken: {out_pdf}")

    c = canvas.Canvas(str(out_pdf), pagesize=(A4_W, A4_H))

    sample_svg = card_svg(entries[0][0], entries[0][1])
    with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
        tmp.write(sample_svg)
        tmp.flush()
        d0 = svg2rlg(tmp.name)
    w0, h0 = d0.width, d0.height
    s0, dx0, dy0 = scale_and_center(w0, h0)

    for p in range(num_pages):
        batch = entries[p * per_page : (p + 1) * per_page]
        for i, (code13, name) in enumerate(batch):
            col = i % COLS
            row = i // COLS

            x_left, y_bot = page_xy(col, row, FRONT_PRINT_SHIFT_X, FRONT_PRINT_SHIFT_Y)

            svg_text = card_svg(code13, name)
            with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
                tmp.write(svg_text)
                tmp.flush()
                drawing = svg2rlg(tmp.name)

            drawing.scale(s0, s0)

            if DEBUG_FRAMES:
                c.rect(x_left, y_bot, CARD_W, CARD_H)

            renderPDF.draw(drawing, c, x_left + dx0, y_bot + dy0)

        c.showPage()

    c.save()
    try:
        os.startfile(out_pdf)
    except Exception:
        pass
    print("✔ FRONT bundel klaar.\n")


def generate_all_back():
    df = load_members_df()
    if df is None:
        return

    entries = [(str(r[CODE_COL]).strip(), str(r[NAME_COL]).strip()) for _, r in df.iterrows()]
    if not entries:
        print("❌ Geen leden in leden.xlsx.")
        return

    xlsx_path = EXCEL_PATH
    manual_dates = load_back_dates(xlsx_path) if Path(xlsx_path).exists() else None
    if manual_dates and manual_dates[0].year != SEASON_START_YEAR:
        manual_dates = None

    back_svg_text = back_card_svg(SEASON_START_YEAR, manual_dates)

    per_page = COLS * ROWS
    num_pages = math.ceil(len(entries) / per_page)

    out_pdf = OUTPUT_DIR / f"Lidkaarten_A4_BACK_all_{SEASON_START_YEAR}-{SEASON_START_YEAR+1}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    print(f"📄 BACK A4 bundel maken: {out_pdf}")

    c = canvas.Canvas(str(out_pdf), pagesize=(A4_W, A4_H))

    with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
        tmp.write(back_svg_text)
        tmp.flush()
        b0 = svg2rlg(tmp.name)
    w0, h0 = b0.width, b0.height
    s0, dx0, dy0 = scale_and_center(w0, h0)

    for p in range(num_pages):
        c.saveState()
        c.translate(BACK_IMPOSE_X_SHIFT, 0)

        for i in range(per_page):
            col = i % COLS
            row = i // COLS
            x_left, y_bot = page_xy(col, row)

            with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
                tmp.write(back_svg_text)
                tmp.flush()
                drawing = svg2rlg(tmp.name)

            drawing.scale(s0, s0)

            if DEBUG_FRAMES:
                c.rect(x_left, y_bot, CARD_W, CARD_H)

            renderPDF.draw(drawing, c, x_left + dx0, y_bot + dy0)

        c.restoreState()
        c.showPage()

    c.save()
    try:
        os.startfile(out_pdf)
    except Exception:
        pass
    print("✔ BACK bundel klaar.\n")


def cleanup_outputs():
    patterns = ["*.pdf"]
    removed = 0
    for pat in patterns:
        for f in OUTPUT_DIR.glob(pat):
            try:
                f.unlink()
                removed += 1
            except Exception:
                pass
    print(f"🧹 Opruiming klaar: {removed} bestanden verwijderd.\n")


# def open_output_folders():
#     try:
#         os.startfile(str(OUTPUT_DIR))
#     except Exception:
#         pass


def testprint_four_cards():
    df = load_members_df()
    if df is None or df.empty:
        print("❌ Geen leden.")
        return

    entries = [(str(r[CODE_COL]).strip(), str(r[NAME_COL]).strip()) for _, r in df.head(4).iterrows()]
    if not entries:
        print("❌ Geen leden.")
        return

    out_pdf = OUTPUT_DIR / f"TEST_4cards_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    c = canvas.Canvas(str(out_pdf), pagesize=(A4_W, A4_H))

    sample_svg = card_svg(entries[0][0], entries[0][1])
    with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
        tmp.write(sample_svg)
        tmp.flush()
        d0 = svg2rlg(tmp.name)
    w0, h0 = d0.width, d0.height
    s0, dx0, dy0 = scale_and_center(w0, h0)

    for i, (code13, name) in enumerate(entries):
        col = i % COLS
        row = i // COLS
        x_left, y_bot = page_xy(col, row, FRONT_PRINT_SHIFT_X, FRONT_PRINT_SHIFT_Y)

        svg_text = card_svg(code13, name)
        with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
            tmp.write(svg_text)
            tmp.flush()
            drawing = svg2rlg(tmp.name)

        drawing.scale(s0, s0)
        if DEBUG_FRAMES:
            c.rect(x_left, y_bot, CARD_W, CARD_H)
        renderPDF.draw(drawing, c, x_left + dx0, y_bot + dy0)

    c.save()
    try:
        os.startfile(out_pdf)
    except Exception:
        pass
    print("✔ Testprint 4 kaarten klaar.\n")


def main():
    while True:
        print(
            f"""
==============================
THE WHISKIES - LIDKAARTEN MENU
Seizoen {SEASON_START_YEAR}-{SEASON_START_YEAR+1}
Layout: COLS={COLS} ROWS={ROWS} GAP_X={GAP_X/MM:.1f}mm GAP_Y={GAP_Y/MM:.1f}mm MARGIN={PAGE_MARGIN/MM:.1f}mm
==============================
1) Print 1 lidkaart (single, positie 1–10)
2) Print alle lidkaarten duplex (Lidkaartenduplex.py)
3) Ledenlijst tonen
4) Info over lid
5) Print alle FRONT lidkaarten (A4 bundel)
6) Print alle BACK lidkaarten (A4 bundel)
7) Output opruimen (PDF)
9) Live preview kaart (preview_card.py)
10) Testprint 4 kaarten
11) Nieuw lid toevoegen (nieuw_lid.py)
12) Afsluiten
"""
        )
        choice = input("> ").strip()

        if choice == "1":
            name = input("Naam: ").strip()
            try:
                pos = int(input("Positie (1–10): ").strip())
                if not 1 <= pos <= 10:
                    raise ValueError
            except ValueError:
                print("❌ Ongeldige positie (1–10).")
                continue
            generate_single_card(pos, name)

        elif choice == "2":
            subprocess.run([sys.executable, "Lidkaartenduplex.py"])

        elif choice == "3":
            list_members()

        elif choice == "4":
            member_info()

        elif choice == "5":
            generate_all_front()

        elif choice == "6":
            generate_all_back()

        elif choice == "7":
            cleanup_outputs()

        # elif choice == "8":
        #     open_output_folders()

        elif choice == "9":
           subprocess.run([sys.executable, "preview_card.py"])

        elif choice == "10":
            testprint_four_cards()

        elif choice == "11":
            subprocess.run([sys.executable, "nieuw_lid.py"])

        # elif choice == "12":
        #     subprocess.run([sys.executable, "menu_barcodes.py"])

        elif choice == "12":
            print("Programma afgesloten.")
            break
        else:
            print("❌ Ongeldige keuze.\n")


if __name__ == "__main__":
>>>>>>> 14b142486c61fce67c54e7dc87a5c29fdb29e6d5
    main()