# -*- coding: utf-8 -*-
import datetime
import os
import math
import subprocess
import sys
from pathlib import Path
import pandas as pd
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from tempfile import NamedTemporaryFile
from config import EXCEL_PATH, SHEET, CODE_COL, NAME_COL
from colorama import init, Fore, Back, Style
init(autoreset=True)

BASE_DIR = Path(__file__).resolve().parent

# =========================================================
# Belangrijk: we hergebruiken de werkende "LK" module uit print_single_card
# zodat je niet meer moet sukkelen met de juiste Lidkaart_*.py naam.
# =========================================================
from print_single_card import generate_single_card, LK

DEBUG = False
if DEBUG:
    print("✅ MENU gebruikt LK:", LK.__file__)
    print("✅ MENU seizoen:", LK.SEASON_START_YEAR, "-", LK.SEASON_START_YEAR + 1)
    print("✅ MENU header:", getattr(LK, "HEADER_TEXT", None))


card_svg = LK.card_svg
back_card_svg = LK.back_card_svg
SEASON_START_YEAR = LK.SEASON_START_YEAR

# Excel loader (back-datums)
from excel_loader import load_back_dates

# ---------- A4 GRID ----------
MM = 72.0 / 25.4
A4_W, A4_H = 595, 842
GRID_COLS, GRID_ROWS = 2, 5
PAGE_MARGIN = 18
CELL_MARGIN = 6

# ---------- Excel kolomnamen ----------
COL_CODE = CODE_COL
COL_NAME = NAME_COL


# ----------------------------------------------------
#  HULP: leden.xlsx laden
# ----------------------------------------------------
def load_members_df():
    xlsx_path = BASE_DIR / "leden.xlsx"
    if not xlsx_path.exists():
        print(f"❌ leden.xlsx niet gevonden in {BASE_DIR}")
        return None
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET, dtype=str)
        df.columns = df.columns.astype(str).str.strip()

        # snelle validatie
        missing = [c for c in (COL_CODE, COL_NAME) if c not in df.columns]
        if missing:
            print("❌ Verkeerde kolomnamen in leden.xlsx.")
            print("   Gevonden kolommen:", list(df.columns))
            print("   Verwacht:", [COL_CODE, COL_NAME])
            return None

        return df
    except Exception as e:
        print(f"❌ Fout bij lezen van leden.xlsx: {e}")
        return None


# ----------------------------------------------------
#  3) LEDEN LIJST
# ----------------------------------------------------
def list_members():
    df = load_members_df()
    if df is None:
        return
    print("\n===== LEDENLIJST =====")
    for i, r in df.iterrows():
        print(f"{i+1:3d}. {str(r[COL_CODE]).strip()}   {str(r[COL_NAME]).strip()}")
    print("======================\n")


# ----------------------------------------------------
#  4) INFO OVER ÉÉN LID
# ----------------------------------------------------
def member_info():
    df = load_members_df()
    if df is None:
        return

    needle = input("Naam (of deel): ").strip().lower()
    found = df[df[COL_NAME].astype(str).str.lower().str.contains(needle, na=False)]

    if found.empty:
        print("❌ Geen lid gevonden.")
        return

    print("\n===== INFO =====")
    for idx, r in found.iterrows():
        print(f"Index : {idx+1}")
        print(f"Naam  : {str(r[COL_NAME]).strip()}")
        print(f"Code  : {str(r[COL_CODE]).strip()}")
        print("----------------------")
    print("================\n")


# ----------------------------------------------------
#  5) FRONT A4 BUNDEL (snijvriendelijk voor 85x54)
# ----------------------------------------------------

print("✅ TEST: generate_all_front NIEUWE FIX draait")

def generate_all_front():
    df = load_members_df()
    if df is None:
        return

    entries = [(str(r[COL_CODE]).strip(), str(r[COL_NAME]).strip()) for _, r in df.iterrows()]
    if not entries:
        print("❌ Geen leden in leden.xlsx.")
        return

    from datetime import datetime
    # out_pdf = BASE_DIR / f"Lidkaarten_A4_FRONT_all_{SEASON_START_YEAR}-{SEASON_START_YEAR+1}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    out_pdf = BASE_DIR / f"TEST_NEW_LAYOUT_FRONT_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    print(f"📄 FRONT A4 bundel maken: {out_pdf}")

    c = canvas.Canvas(str(out_pdf), pagesize=(A4_W, A4_H))
    per_page = GRID_COLS * GRID_ROWS
    num_pages = math.ceil(len(entries) / per_page)

    # ✅ kaartformaat uit LK (moet 85x54 zijn)
    CARD_W = LK.CARD_W
    CARD_H = LK.CARD_H

    # ✅ echte middenruimte (0 = 1 snede in midden)
    GAP_X = 20 * LK.MM     # zet evt. op 1*LK.MM als je 1 mm speling wil
    print("✅ DEBUG GAP_X (mm) =", GAP_X / MM)
    
    # verticale verdeling: we gebruiken PAGE_MARGIN boven/onder en verdelen de rest gelijk
    usable_h = A4_H - 2 * PAGE_MARGIN
    gap_y_auto = (usable_h - GRID_ROWS * CARD_H) / (GRID_ROWS - 1)
    if gap_y_auto < 0:
        print("❌ Past niet in de hoogte: verlaag GRID_ROWS of PAGE_MARGIN.")
        return

    # horizontaal: centreer 2 kaarten + middenruimte op A4
    total_w = 2 * CARD_W + GAP_X
    x0 = (A4_W - total_w) / 2

    for p in range(num_pages):
        batch = entries[p * per_page : (p + 1) * per_page]

        for i, (code13, name) in enumerate(batch):
            svg_text = card_svg(code13, name)

            col = i % GRID_COLS
            row = i // GRID_COLS

            with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
                tmp.write(svg_text)
                tmp.flush()
                drawing = svg2rlg(tmp.name)

            w0, h0 = drawing.width, drawing.height

            # ✅ NOOIT vergroten
            s = min(CARD_W / w0, CARD_H / h0, 1.0)

            # ✅ vaste positie: geen cell-centering meer
            x_left = x0 + col * (CARD_W + GAP_X)
            y_bot  = A4_H - PAGE_MARGIN - (row + 1) * CARD_H - row * gap_y_auto

            drawing.scale(s, s)
            c.rect(x_left, y_bot, CARD_W, CARD_H)  # dun kader rond kaart
            renderPDF.draw(drawing, c, x_left, y_bot)

        c.showPage()

    c.save()
    os.startfile(out_pdf)
    print("✔ FRONT bundel klaar.\n")


# ------------------------------------------
# 6) BACK A4 BUNDEL  (met Excel datums indien ingevuld)
# ------------------------------------------
def generate_all_back():
    df = load_members_df()
    if df is None:
        return

    # Leden lijst nodig voor aantal pagina’s
    entries = [(str(r[COL_CODE]).strip(), str(r[COL_NAME]).strip()) for _, r in df.iterrows()]
    if not entries:
        print("❌ Geen leden in leden.xlsx.")
        return

    # back-datums inladen (Excel override)
    xlsx_path = BASE_DIR / "leden.xlsx"

    manual_dates = load_back_dates(xlsx_path)

# --- SAFETY: Excel-datums alleen gebruiken als ze bij dit seizoen horen ---
    if manual_dates and manual_dates[0].year != SEASON_START_YEAR:
        print(
        f"⚠️ Excel-datums ({manual_dates[0].year}) "
        f"horen niet bij seizoen {SEASON_START_YEAR}-{SEASON_START_YEAR+1} → genegeerd."
    )
        manual_dates = None

    if manual_dates:
        print("📅 Back-datums uit Excel geladen.")
    else:
        print("ℹ️ Geen manuele datums in Excel → automatische berekening.")

    svg_back = back_card_svg(SEASON_START_YEAR, manual_dates)

    out_pdf = BASE_DIR / f"Lidkaarten_A4_BACK_all_{SEASON_START_YEAR}-{SEASON_START_YEAR+1}.pdf"
    print(f"📄 BACK A4 bundel maken: {out_pdf}")

    c = canvas.Canvas(str(out_pdf), pagesize=(A4_W, A4_H))

    per_page = GRID_COLS * GRID_ROWS
    num_pages = math.ceil(len(entries) / per_page)

    for p in range(num_pages):
        for i in range(per_page):
            cell_w = (A4_W - 2 * PAGE_MARGIN) / GRID_COLS
            cell_h = (A4_H - 2 * PAGE_MARGIN) / GRID_ROWS

            col = i % GRID_COLS
            row = i // GRID_COLS

            with NamedTemporaryFile("w+", suffix=".svg", delete=False, encoding="utf-8") as tmp:
                tmp.write(svg_back)
                tmp.flush()
                drawing = svg2rlg(tmp.name)

            w0, h0 = drawing.width, drawing.height
            s = min(
                (cell_w - 2 * CELL_MARGIN) / w0,
                (cell_h - 2 * CELL_MARGIN) / h0
            )

            x_left = PAGE_MARGIN + col * cell_w + (cell_w - w0 * s) / 2
            y_bot  = A4_H - (PAGE_MARGIN + (row + 1) * cell_h) + (cell_h - h0 * s) / 2

            drawing.scale(s, s)
            renderPDF.draw(drawing, c, x_left, y_bot)

        c.showPage()

    c.save()
    os.startfile(out_pdf)
    print("✔ BACK A4 bundel klaar.\n")


# ----------------------------------------------------
#  7) OPSCHONEN
# ----------------------------------------------------
def cleanup_outputs():
    folders = ["kaartjes_pdf", "single_pdf", "kaartjes_svg"]
    print("🧹 Opruimen…")
    for fname in folders:
        folder = BASE_DIR / fname
        if folder.exists():
            for x in folder.iterdir():
                try:
                    if x.is_file():
                        x.unlink()
                except:
                    pass
            print(f" - {folder} leeggemaakt")
        else:
            print(f" - {folder} bestaat niet (overgeslagen)")
    print("✔ Alles opgeruimd.\n")


# ----------------------------------------------------
#  8) FOLDERS OPENEN
# ----------------------------------------------------
def open_output_folders():
    for fname in ["kaartjes_pdf", "single_pdf"]:
        path = BASE_DIR / fname
        if path.exists():
            os.startfile(path)
            print(f"📂 Geopend: {path}")
        else:
            print(f"⚠️ Map bestaat niet: {path}")
    print("✔ Klaar.\n")


# ----------------------------------------------------
#  10) TESTPRINT 4 kaarten
# ----------------------------------------------------
def testprint_four_cards():
    df = load_members_df()
    if df is None:
        return

    if len(df) < 4:
        print("❌ Minder dan 4 leden.")
        return

    sample = df.sample(4).reset_index(drop=True)
    positions = [1, 2, 3, 4]

    print("\n🖨 TESTPRINT – 4 kaartjes:")
    for i in range(4):
        name = str(sample.loc[i, COL_NAME])
        pos = positions[i]
        print(f" - {name} op positie {pos}")
        generate_single_card(pos, name)

    print("\n✔ Testprint klaar.\n")


# ----------------------------------------------------
#  MENU
# ----------------------------------------------------
def main():
    while True:
        print(f"""
========================================================
      THE WHISKIES – LIDKAART PRINT MENU {SEASON_START_YEAR}-{SEASON_START_YEAR+1}
========================================================
Basisdirectory:
{BASE_DIR}

1) Print één kaartje  (recto + verso)
2) Print alle lidkaarten duplex (Lidkaartenduplex.py)
3) Toon lijst van alle leden
4) Toon info over één lid
5) Genereer FRONT A4 bundel
6) Genereer BACK  A4 bundel
7) Opschonen
8) Open output-mappen
9) Stoppen
10) TESTPRINT – 4 kaartjes
11) Nieuw lid toevoegen
12) Barcode menu
--------------------------------------------------------
Maak je keuze (1–12): """)
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

        elif choice == "8":
            open_output_folders()

        elif choice == "9":
            print("Programma afgesloten.")
            break

        elif choice == "10":
            testprint_four_cards()

        elif choice == "11":
            subprocess.run([sys.executable, "nieuw_lid.py"])
            again = input("Wil je meteen een lidkaart printen? (j/n): ").strip().lower()
            if again == "j":
                name = input("Naam: ").strip()
                try:
                    pos = int(input("Positie (1–10): ").strip())
                    if not 1 <= pos <= 10:
                        raise ValueError
                except ValueError:
                    print("❌ Ongeldige positie (1–10).")
                    continue
                generate_single_card(pos, name)

        elif choice == "12":
            subprocess.run([sys.executable, "menu_barcodes.py"])

        else:
            print("❌ Ongeldige keuze.\n")
if __name__ == "__main__":
    main()