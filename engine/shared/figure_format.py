from __future__ import annotations

from typing import Any

from engine.shared.constants import GOST_LINE_SPACING_MAIN, GOST_MAIN_FONT_NAME, GOST_MAIN_FONT_SIZE_PT


_FIGURE_PARAGRAPH_FORMAT: dict[str, Any] = {
    "alignment": "CENTER",
    "first_line_indent_cm": 0.0,
}

_FIGURE_CAPTION_FORMAT: dict[str, Any] = {
    "alignment": "CENTER",
    "first_line_indent_cm": 0.0,
    "line_spacing": GOST_LINE_SPACING_MAIN,
    "font_name": GOST_MAIN_FONT_NAME,
    "font_size_pt": GOST_MAIN_FONT_SIZE_PT,
    "bold": False,
    "italic": False,
    "underline": False,
}


def figure_paragraph_format() -> dict[str, Any]:
    return dict(_FIGURE_PARAGRAPH_FORMAT)


def figure_caption_format() -> dict[str, Any]:
    return dict(_FIGURE_CAPTION_FORMAT)


def is_center_alignment(alignment: object) -> bool:
    value = str(alignment or "").upper()
    return "CENTER" in value or "(1)" in value
