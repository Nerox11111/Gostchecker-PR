from __future__ import annotations

import re

from engine.shared.regex_patterns import ABBREV_LIST_LINE_RE
from engine.shared.figure_caption_utils import is_figure_caption_text
from engine.shared.listing_utils import is_listing_caption_text
from engine.shared.list_line_utils import is_any_list_line


STRUCTURAL_TITLES = {
    "СОДЕРЖАНИЕ",
    "ВВЕДЕНИЕ",
    "ЗАКЛЮЧЕНИЕ",
    "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ",
    "СПИСОК ЛИТЕРАТУРЫ",
    "ПРИЛОЖЕНИЕ",
    "ПРИЛОЖЕНИЯ",
}

HEADING_RE = re.compile(r"^\s*\d+(\.\d+)*\s+[^\n]+$")


def is_structural_heading(text: str) -> bool:
    t = (text or "").strip().upper()
    if not t:
        return False
    if t in STRUCTURAL_TITLES:
        return True
    if HEADING_RE.match(t):
        return True
    return False


def is_listing_caption(text: str) -> bool:
    return is_listing_caption_text(text)


def is_abbrev_line(text: str) -> bool:
    return bool(ABBREV_LIST_LINE_RE.match((text or "").strip()))


def is_zero_indent_exception(text: str) -> bool:
    t = text or ""
    return (
        is_figure_caption_text(t)
        or is_listing_caption(t)
        or is_abbrev_line(t)
        or is_structural_heading(t)
        or t.strip().startswith("Таблица ")
    )

