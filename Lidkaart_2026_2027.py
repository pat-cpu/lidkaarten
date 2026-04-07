# -*- coding: utf-8 -*-
"""
Lidkaart_2026_2027.py
ENIGE bron van waarheid voor layout (front + back)

Opkuis gedaan:
- Geen dubbele PRINT LAYOUT blokken
- Geen dubbele DEBUG_FRAMES / PRINT_COLS / PRINT_ROWS / PAGE_MARGIN_MM / GAP_* / SCALE_MAX_1
- Verticale scheidingslijn staat 1x, met config bovenaan
- Geen rare self-imports
"""

from __future__ import annotations

from pathlib import Path
import base64
import calendar
import io
from datetime import date, timedelta

# Excel loader: gebruikt voor datums (wordt door andere scripts gebruikt)
from excel_loader import load_back_dates  # noqa: F401 (mag blijven voor compat)

BASE_DIR = Path(__file__).resolve().parent

# ------------------------------------------------------------
# SEIZOEN
# ------------------------------------------------------------
SEASON_START_YEAR = 2026
SEASON_END_YEAR = SEASON_START_YEAR + 1

HEADER_TEXT = f"Lidkaart {SEASON_START_YEAR} - {SEASON_END_YEAR}"
PRICE_TEXT = " 30€"

# ------------------------------------------------------------
# ALGEMENE CONSTANTEN (85x54 mm)
# ------------------------------------------------------------
MM = 72.0 / 25.4

# PRINT KALIBRATIE FRONT
# Alleen de FRONT wordt hiermee verschoven bij printen
FRONT_PRINT_SHIFT_X = -3 * MM   # front 2 mm naar links
FRONT_PRINT_SHIFT_Y = 1 * MM

# CREDITCARD FORMAAT
CARD_W = 85 * MM
CARD_H = 54 * MM

PADDING = 9                            # De binnenruimte tussen de rand van de kaart en de inhoud

FONT = "DejaVu Sans, Arial"

# Barcode
BARCODE_WIDTH = 95
BARCODE_HEIGHT = 40

# Logo
LOGO_W = 25 * MM
#LOGO_PATH = BASE_DIR / "logo.png"      #LOGO_PATH = BASE_DIR / "afbeeldingen" / "logo.png"	#Indien je een andere afbeelding gebruikt				
LOGO_PATH = BASE_DIR / "assets" / "logo.png"                                      					
# QR
QR_SIZE = 36
QR_URL = "https://kaartclub-the-whiskies.webnode.be/"

# Posities / offsets
HEADER_OFFSET_Y = 10 * MM
PRICE_OFFSET_Y = 3 * MM      # hoe kleiner getal hoe hoger
PRICE_OFFSET_X = 15          # hoe hoger getal hoe meer naar rechts
NAME_OFFSET_X = -4
NAME_OFFSET_Y = 7 * MM
QR_OFFSET_X = 6
QR_OFFSET_Y = -15

CONTACT_1 = "Gsm Patrick: 0486/26.23.42"    # om deze twee regels hoger of lager te zetten zie lijn 289-290
CONTACT_2 = "Walter: 0475/24.05.15"

# ------------------------------------------------------------
# VERTICALE SCHEIDINGSLIJN (FRONT)
# ------------------------------------------------------------
FRONT_SEP_LINE_ENABLED = True           #Groen lijntje  True = tonen  False = niet tonen
FRONT_SEP_LINE_LENGTH_MM = 20.0
FRONT_SEP_LINE_OFFSET_LEFT_MM = 60.0    #groter getal = meer naar rechts
FRONT_SEP_LINE_BOTTOM_MARGIN_MM = 5.0   #groter getal = start hoger vanaf de onderrand
FRONT_SEP_LINE_COLOR = "#008000"
FRONT_SEP_LINE_WIDTH_PT = 1.0

# ------------------------------------------------------------
# BACK instellingen
# ------------------------------------------------------------
BACK_WEEKDAY_NAME = "MAANDAG"  #vaste tekst
BACK_DEFAULT_TIME = "13u30"
BACK_JANUARY_TIME = "13u00"

BACK_HEADER_FONT = 13
BACK_SUB_FONT = 11          #Lettergrootte
BACK_DATES_FONT = 10
BACK_NOTE_FONT = 8

BACK_HEADER_OFFSET_Y = 26
BACK_BLOCK_GAP = 20
BACK_LINE_GAP = 14     #Dit is de afstand tussen de lijnen met datums of tekstregels.
BACK_NOTE_GAP = 14    #Dit is de afstand naar de kleine nota of voetnoot.
BACK_HEADER_TO_SUB_GAP = 22    #de afstand tussen de hoofdtitel en de subtitel.

# Duplex fine-tuning shift voor BACK
BACK_IMPOSE_X_SHIFT = 2.3 * MM        #als de voorkant goed staat, maar de achterkant net een beetje te veel links of rechts zit, dan corrigeer je dat hier.
                                      # Positief getal schuift de achterkant naar rechts, negatief getal schuift de achterkant naar links.
# Kaart-impositie / papier
A4_W, A4_H = 595, 842  # A4 portrait (points) afmeting A4 in punyen

# =========================================================
# PRINT / PAGE LAYOUT
# =========================================================
PRINT_COLS = 2     # Aantal lidkaarten per blad
PRINT_ROWS = 5

# buitenmarge (mm) rondom op A4
PAGE_MARGIN_MM = 6.0   # buitenmarge rondom blad

# tussenruimte (mm) tussen kaartvakken
GAP_X_MM = 0.0
GAP_Y_MM = 0.0

# schaal nooit vergroten
SCALE_MAX_1 = True

# debug kaders rond kaartvakken
DEBUG_FRAMES = False  # zet False voor definitieve print

# Snijlijnen (crop marks)
CROP_MARKS = True           # Tonen of niet tonen
CROP_LEN_MM = 3.0
CROP_GAP_MM = 0.8           # Afstand tussen de kaart en het begin van de snijlijn.				
CROP_STROKE_PT = 0.25       # Dikte van de snijlijnen.

# ---------------------------------------------------------
# COMPAT (oudere scripts)
# ---------------------------------------------------------
GRID_COLS, GRID_ROWS = PRINT_COLS, PRINT_ROWS     # dit zijn interne berekeningen, niet aankomen
PAGE_MARGIN = PAGE_MARGIN_MM * MM
GAP_X = GAP_X_MM * MM
GAP_Y = GAP_Y_MM * MM
CELL_MARGIN = 0

# ------------------------------------------------------------
# UTILITIES (PNG -> data uri)
# ------------------------------------------------------------
def png_size(p: Path):
    """Lees PNG afmetingen — nodig voor correct schalen logo."""
    try:
        with open(p, "rb") as f:
            if f.read(8) != b"\x89PNG\r\n\x1a\n":
                return None
            f.read(4)
            if f.read(4) != b"IHDR":
                return None
            import struct
            w, h = struct.unpack(">II", f.read(8))
            return w, h
    except Exception:
        return None


def file_to_data_uri_png(p: Path) -> str | None:
    """Converteer PNG naar base64 data-uri."""
    if not p.exists():
        return None
    try:
        from PIL import Image
        im = Image.open(p).convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        rgb = bg.convert("RGB")
        buf = io.BytesIO()
        rgb.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/png;base64,{b64}"
    except Exception:
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        return f"data:image/png;base64,{b64}"


def logo_image_fragment():
    """Zet logo PNG om naar SVG-fragment."""
    if not LOGO_PATH.exists():
        return None
    wh = png_size(LOGO_PATH)
    if not wh:
        return None
    w_px, h_px = wh
    ratio = h_px / float(w_px)
    logo_w = LOGO_W
    logo_h = logo_w * ratio
    uri = file_to_data_uri_png(LOGO_PATH)
    if not uri:
        return None
    frag = f'<image xlink:href="{uri}" width="{logo_w:.2f}" height="{logo_h:.2f}"/>'
    return frag, logo_w, logo_h


# ------------------------------------------------------------
# BARCODE (EAN13)  genereren
# ------------------------------------------------------------
A = {'0':'0001101','1':'0011001','2':'0010011','3':'0111101','4':'0100011',
     '5':'0110001','6':'0101111','7':'0111011','8':'0110111','9':'0001011'}
B = {'0':'0100111','1':'0110011','2':'0011011','3':'0100001','4':'0011101',
     '5':'0111001','6':'0000101','7':'0010001','8':'0001001','9':'0010111'}
C = {'0':'1110010','1':'1100110','2':'1101100','3':'1000010','4':'1011100',
     '5':'1001110','6':'1010000','7':'1000100','8':'1001000','9':'1110100'}
PARITY = {
    0:"AAAAAA", 1:"AABABB", 2:"AABBAB", 3:"AABBBA", 4:"ABAABB",
    5:"ABBAAB", 6:"ABBBAA", 7:"ABABAB", 8:"ABABBA", 9:"ABBABA"
}


def encode_bits(code13: str) -> str:
    first = int(code13[0])
    left = code13[1:7]
    right = code13[7:13]

    bits = "101"
    pattern = PARITY[first]

    for i, d in enumerate(left):
        bits += A[d] if pattern[i] == "A" else B[d]

    bits += "01010"

    for d in right:
        bits += C[d]

    bits += "101"
    return bits


def barcode_g(code13: str, max_w: float, bars_h: float):
    bits = encode_bits(code13)

    module = 1
    total_w = len(bits) * module + 20
    scale = min(1.0, max_w / total_w)

    parts = [f'<g transform="scale({scale})">']
    for i, b in enumerate(bits):
        if b == "1":
            y = 5
            h = bars_h
            if i < 3 or (45 <= i < 50) or i >= len(bits) - 3:
                y = 0
                h = bars_h + 8
            parts.append(f'<rect x="{10+i*module}" y="{y}" width="{module}" height="{h}" fill="black"/>')

    parts.append(
        f'<text x="{total_w/2}" y="{bars_h+14}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="10">{code13}</text>'
    )
    parts.append("</g>")
    return "\n".join(parts)


# ------------------------------------------------------------
# FRONT SVG   Aanpassingen voorkant lidkaart
# ------------------------------------------------------------
def card_svg(code13: str, full_name: str, qr_payload=None):
    qr_payload = qr_payload or QR_URL
    bar_g = barcode_g(code13, BARCODE_WIDTH, BARCODE_HEIGHT)
    right_x = CARD_W - PADDING

    logo_pack = logo_image_fragment()
    logo_svg = ""
    logo_h = 0.0
    if logo_pack:
        logo_svg, _, logo_h = logo_pack

    header_y = PADDING + logo_h + HEADER_OFFSET_Y
    price_y = header_y + 16 + PRICE_OFFSET_Y
    name_y = CARD_H / 2

    try:
        import segno
        qr = segno.make(qr_payload, error="m")
        buf = io.BytesIO()
        qr.save(buf, kind="png", scale=10, border=2)
        qr_uri = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"
    except Exception:
        qr_uri = None

    contact1_y = CARD_H - PADDING - 18
    contact2_y = CARD_H - PADDING - 6

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '    # Maakt het SVG-canvas aan met kaartbreedte en kaarthoogte.
        f'width="{CARD_W}" height="{CARD_H}">'
    ]

    parts.append('<rect width="100%" height="100%" rx="6" ry="6" fill="white"/>')    # Volledige witte achtergrond met afgeronde hoeken.

    if logo_svg:
        parts.append(f'<g transform="translate({PADDING},{PADDING})">{logo_svg}</g>')

    if FRONT_SEP_LINE_ENABLED:
        sep_len = FRONT_SEP_LINE_LENGTH_MM * MM
        sep_left = FRONT_SEP_LINE_OFFSET_LEFT_MM * MM
        sep_bottom = FRONT_SEP_LINE_BOTTOM_MARGIN_MM * MM

        x_line = CARD_W - sep_left
        y2 = CARD_H - sep_bottom
        y1 = y2 - sep_len

        parts.append(
            f'<line x1="{x_line:.2f}" y1="{y1:.2f}" x2="{x_line:.2f}" y2="{y2:.2f}" '
            f'stroke="{FRONT_SEP_LINE_COLOR}" stroke-width="{FRONT_SEP_LINE_WIDTH_PT}" />'
        )

    parts.append(
        f'<text x="{PADDING}" y="{header_y}" font-family="{FONT}" font-size="12" font-weight="bold">{HEADER_TEXT}</text>'
    )
    parts.append(
        f'<text x="{PADDING + PRICE_OFFSET_X}" y="{price_y}" font-family="{FONT}" font-size="14" font-weight="bold">{PRICE_TEXT}</text>'
    )

    parts.append(f'<g transform="translate({right_x - BARCODE_WIDTH}, {PADDING+2})">{bar_g}</g>')

    parts.append(
        f'<text x="{right_x + NAME_OFFSET_X}" y="{name_y + NAME_OFFSET_Y}" text-anchor="end" '
        f'font-family="{FONT}" font-size="12" font-weight="bold">{full_name}</text>'
    )

    if qr_uri:
        parts.append(
            f'<image xlink:href="{qr_uri}" x="{PADDING+QR_OFFSET_X}" y="{CARD_H-PADDING-QR_SIZE+QR_OFFSET_Y}" '
            f'width="{QR_SIZE}" height="{QR_SIZE}"/>'
        )
    else:
        parts.append(
            f'<rect x="{PADDING+QR_OFFSET_X}" y="{CARD_H-PADDING-QR_SIZE+QR_OFFSET_Y}" width="{QR_SIZE}" height="{QR_SIZE}" '
            f'fill="none" stroke="black"/>'
        )

    parts.append(
        f'<text x="{right_x}" y="{contact1_y}" text-anchor="end" font-family="{FONT}" font-size="10">{CONTACT_1}</text>'
    )
    parts.append(
        f'<text x="{right_x}" y="{contact2_y}" text-anchor="end" font-family="{FONT}" font-size="10">{CONTACT_2}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


# ------------------------------------------------------------
# BACK SVG
# ------------------------------------------------------------
MONTHS = {
    1:"januari",2:"februari",3:"maart",4:"april",5:"mei",6:"juni",
    7:"juli",8:"augustus",9:"september",10:"oktober",11:"november",12:"december"
}
MONTHS_ABBR = {
    1:"jan.",2:"feb.",3:"mrt.",4:"apr.",5:"mei",6:"jun.",
    7:"jul.",8:"aug.",9:"sep.",10:"okt.",11:"nov.",12:"dec."
}


def format_date_nl(d: date, abbr: bool = False) -> str:
    m = MONTHS_ABBR[d.month] if abbr else MONTHS[d.month]
    return f"{d.day} {m}"


def easter_sunday(year: int) -> date:
    """Meeus/Jones/Butcher algorithm."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19*a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*l) // 451
    month = (h + l - 7*m + 114) // 31
    day = ((h + l - 7*m + 114) % 31) + 1
    return date(year, month, day)


def belgian_public_holidays(year: int) -> set[date]:
    easter = easter_sunday(year)
    easter_monday = easter + timedelta(days=1)
    ascension = easter + timedelta(days=39)
    whit_monday = easter + timedelta(days=50)

    return {
        date(year, 1, 1),
        easter_monday,
        date(year, 5, 1),
        ascension,
        whit_monday,
        date(year, 7, 21),
        date(year, 8, 15),
        date(year, 11, 1),
        date(year, 11, 11),
        date(year, 12, 25),
    }


def is_holiday_be(d: date) -> bool:
    return d in belgian_public_holidays(d.year)


BACK_N_FOR_MONTHS = {
    9: 4, 10: 4, 11: 4, 12: 3,
    1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4
}


def nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    cal = calendar.Calendar()
    dlist = [d for d in cal.itermonthdates(year, month)
             if d.month == month and d.weekday() == weekday]
    if n == -1:
        return dlist[-1]
    i = n - 1
    return dlist[i] if 0 <= i < len(dlist) else dlist[-1]


def compute_season_dates(year_start: int) -> list[date]:
    out: list[date] = []

    for m in (9, 10, 11, 12):
        n = BACK_N_FOR_MONTHS[m]
        d = nth_weekday_of_month(year_start, m, 0, n)
        if n == 4 and is_holiday_be(d):
            d = nth_weekday_of_month(year_start, m, 0, 3)
        out.append(d)

    for m in (1, 2, 3, 4, 5, 6):
        n = BACK_N_FOR_MONTHS[m]
        d = nth_weekday_of_month(year_start + 1, m, 0, n)
        if n == 4 and is_holiday_be(d):
            d = nth_weekday_of_month(year_start + 1, m, 0, 3)
        out.append(d)

    return out


def back_card_svg(season_start: int, manual_dates=None):
    """
    BACK gebruikt:
    - manual_dates (uit Excel) indien meegegeven
    - anders: automatisch berekende speeldagen
    """
    if manual_dates:
        dates = manual_dates[:10]
    else:
        dates = compute_season_dates(season_start)

    season_end = season_start + 1

    line1 = " - ".join(format_date_nl(d) for d in dates[0:3])
    line2 = " - ".join(format_date_nl(d) for d in dates[3:6])
    line3 = " - ".join(format_date_nl(d) for d in dates[6:10])

    jan_d = dates[4]
    nieuwjaar = f"{format_date_nl(jan_d, abbr=True)} {BACK_JANUARY_TIME} met nieuwjaarsreceptie"

    logo_pack = logo_image_fragment()
    logo_h = logo_pack[2] if logo_pack else 0.0

    cx = CARD_W / 2
    header_y = PADDING + BACK_HEADER_OFFSET_Y + logo_h

    sub_y = header_y + BACK_HEADER_TO_SUB_GAP
    l1_y = sub_y + BACK_BLOCK_GAP
    l2_y = l1_y + BACK_LINE_GAP
    l3_y = l2_y + BACK_LINE_GAP
    note_y = l3_y + BACK_NOTE_GAP

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{CARD_W}" height="{CARD_H}">'
    ]
    parts.append('<rect width="100%" height="100%" rx="6" ry="6" fill="white"/>')

    if logo_pack:
        logo_svg = logo_pack[0]
        parts.append(f'<g transform="translate({PADDING},{PADDING})">{logo_svg}</g>')

    parts.append(
        f'<text x="{cx}" y="{header_y}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="{BACK_HEADER_FONT}" font-weight="bold">Seizoen {season_start} - {season_end}</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{sub_y}" text-anchor="middle" font-family="{FONT}" font-size="{BACK_SUB_FONT}">'
        f'Telkens op {BACK_WEEKDAY_NAME} om {BACK_DEFAULT_TIME}</text>'
    )

    parts.append(f'<text x="{cx}" y="{l1_y}" text-anchor="middle" font-family="{FONT}" font-size="{BACK_DATES_FONT}">{line1}</text>')
    parts.append(f'<text x="{cx}" y="{l2_y}" text-anchor="middle" font-family="{FONT}" font-size="{BACK_DATES_FONT}">{line2}</text>')
    parts.append(f'<text x="{cx}" y="{l3_y}" text-anchor="middle" font-family="{FONT}" font-size="{BACK_DATES_FONT}">{line3}</text>')

    parts.append(
        f'<text x="{cx}" y="{note_y}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="{BACK_NOTE_FONT}" fill="#008000" font-style="italic">{nieuwjaar}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)