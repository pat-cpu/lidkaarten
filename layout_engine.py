# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Layout:
    A4_W: float
    A4_H: float
    CARD_W: float
    CARD_H: float
    COLS: int
    ROWS: int
    PAGE_MARGIN: float   # pt
    GAP_X: float         # pt
    GAP_Y: float         # pt
    SCALE_MAX_1: bool

def build_layout(LK) -> Layout:
    MM = LK.MM
    return Layout(
        A4_W=LK.A4_W,
        A4_H=LK.A4_H,
        CARD_W=LK.CARD_W,
        CARD_H=LK.CARD_H,
        COLS=getattr(LK, "PRINT_COLS", 2),
        ROWS=getattr(LK, "PRINT_ROWS", 5),
        PAGE_MARGIN=getattr(LK, "PAGE_MARGIN_MM", 6.0) * MM,
        GAP_X=getattr(LK, "GAP_X_MM", 0.0) * MM,
        GAP_Y=getattr(LK, "GAP_Y_MM", 0.0) * MM,
        SCALE_MAX_1=getattr(LK, "SCALE_MAX_1", True),
    )

def compute_grid_origin(layout):
    """
    Berekent startpunt (x0,y0) zodat het 2x5 grid perfect gecentreerd staat op A4.
    Hou rekening met PAGE_MARGIN als minimum marge.
    """
    cols = layout.PRINT_COLS
    rows = layout.PRINT_ROWS

    grid_w = cols * layout.CARD_W + (cols - 1) * layout.GAP_X
    grid_h = rows * layout.CARD_H + (rows - 1) * layout.GAP_Y

    avail_w = layout.A4_W - 2 * layout.PAGE_MARGIN
    avail_h = layout.A4_H - 2 * layout.PAGE_MARGIN

    # als je later ooit gaps vergroot en het past net niet: schaal kleiner
    scale = min(avail_w / grid_w, avail_h / grid_h)
    if getattr(layout, "SCALE_MAX_1", True):
        scale = min(scale, 1.0)

    grid_w_s = grid_w * scale
    grid_h_s = grid_h * scale

    x0 = (layout.A4_W - grid_w_s) / 2.0
    y0 = (layout.A4_H - grid_h_s) / 2.0

    return scale, x0, y0 

def page_xy(layout: Layout, col: int, row: int) -> tuple[float, float]:
    """
    col,row zijn 0-based. row=0 is bovenste rij.
    Plaats kaarten in vaste 85x54 vakken, gecentreerd op A4.
    """
    total_w = layout.COLS * layout.CARD_W + (layout.COLS - 1) * layout.GAP_X
    x0 = (layout.A4_W - total_w) / 2

    # hoogte: rijen tegen elkaar + vaste GAP_Y (meestal 0)
    scale, x0, y0 = compute_grid_origin(layout)

    cell_w = layout.CARD_W * scale
    cell_h = layout.CARD_H * scale
    gap_x  = layout.GAP_X * scale
    gap_y  = layout.GAP_Y * scale

    x_left = x0 + col * (cell_w + gap_x)

    # rij 0 bovenaan (logisch bij printen)
    y_bot = y0 + (layout.PRINT_ROWS - 1 - row) * (cell_h + gap_y)

    return x_left, y_bot, scale




def scale_and_center(layout: Layout, w0: float, h0: float) -> tuple[float, float, float]:
    """
    Geeft (s, dx, dy): schaal en offset om SVG te centreren binnen CARD_W/CARD_H.
    """
    s = min(layout.CARD_W / w0, layout.CARD_H / h0)
    if layout.SCALE_MAX_1:
        s = min(s, 1.0)
    dx = (layout.CARD_W - w0 * s) / 2
    dy = (layout.CARD_H - h0 * s) / 2
    return s, dx, dy