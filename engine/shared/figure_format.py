from __future__ import annotations

from typing import Any

from engine.shared.constants import (
    GOST_LEFT_INDENT_CM,
    GOST_LINE_SPACING_MAIN,
    GOST_MAIN_FONT_NAME,
    GOST_MAIN_FONT_SIZE_PT,
    GOST_RIGHT_INDENT_CM,
    GOST_SPACE_AFTER_PT,
    GOST_SPACE_BEFORE_PT,
)


_FIGURE_PARAGRAPH_FORMAT: dict[str, Any] = {
    "alignment": "CENTER",
    "first_line_indent_cm": 0.0,
    "left_indent_cm": GOST_LEFT_INDENT_CM,
    "right_indent_cm": GOST_RIGHT_INDENT_CM,
    "space_before_pt": GOST_SPACE_BEFORE_PT,
    "space_after_pt": GOST_SPACE_AFTER_PT,
}

_FIGURE_CAPTION_FORMAT: dict[str, Any] = {
    "alignment": "CENTER",
    "first_line_indent_cm": 0.0,
    "left_indent_cm": GOST_LEFT_INDENT_CM,
    "right_indent_cm": GOST_RIGHT_INDENT_CM,
    "space_before_pt": GOST_SPACE_BEFORE_PT,
    "space_after_pt": GOST_SPACE_AFTER_PT,
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


def has_figure_image(xml_element: object) -> bool:
    if xml_element is None:
        return False
    xml = xml_element.xml if hasattr(xml_element, "xml") else str(xml_element)
    return "w:drawing" in xml or "w:pict" in xml
