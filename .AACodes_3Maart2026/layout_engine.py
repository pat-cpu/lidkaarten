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

def page_xy(layout: Layout, col: int, row: int) -> tuple[float, float]:
    """
    col,row zijn 0-based. row=0 is bovenste rij.
    Plaats kaarten in vaste 85x54 vakken, gecentreerd op A4.
    """
    total_w = layout.COLS * layout.CARD_W + (layout.COLS - 1) * layout.GAP_X
    x0 = (layout.A4_W - total_w) / 2

    # hoogte: rijen tegen elkaar + vaste GAP_Y (meestal 0)
    y_top = layout.A4_H - layout.PAGE_MARGIN
    x_left = x0 + col * (layout.CARD_W + layout.GAP_X)
    y_bot = y_top - (row + 1) * layout.CARD_H - row * layout.GAP_Y
    return x_left, y_bot

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