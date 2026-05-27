from __future__ import annotations

import re

from engine.models.paragraph_model import ParagraphModel

# Корректный формат: «Рисунок N — Наименование» (без точки в конце).
FIGURE_CAPTION_GOST_RE = re.compile(
    r"^Рисунок\s+\d+\s+[–—]\s+.+[^.]$",
    re.IGNORECASE,
)

# Любая подпись рисунка (в т.ч. неверная «Рис. 1. …»).
FIGURE_CAPTION_ANY_RE = re.compile(
    r"^(Рис\.?|Рисунок)\s*\d+",
    re.IGNORECASE,
)


def is_figure_caption_text(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    return FIGURE_CAPTION_ANY_RE.match(t) is not None


def is_valid_gost_figure_caption(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    return bool(FIGURE_CAPTION_GOST_RE.match(t))


def normalize_figure_caption(text: str) -> str | None:
    """
    Приводит «Рис. 1. Наименование.» / «Рисунок 1 - …» к «Рисунок 1 — Наименование».
    """
    t = (text or "").strip()
    if not t:
        return None

    m = re.match(
        r"^(Рис\.?|Рисунок)\s*(\d+)\s*[\.\-—–:]\s*(.+)$",
        t,
        re.IGNORECASE,
    )
    if not m:
        return None

    num = m.group(2)
    title = m.group(3).strip().rstrip(".")
    if not title:
        return None
    return f"Рисунок {num} — {title}"


def build_blank_after_figure_caption_ids(paragraphs: list[ParagraphModel]) -> set[str]:
    """Пустые строки сразу после подписи рисунка не считаем ошибкой интервалов."""
    skip: set[str] = set()
    prev_was_caption = False
    for p in paragraphs:
        if getattr(p, "in_table", False):
            prev_was_caption = False
            continue
        text = (p.text or "").strip()
        if not text:
            if prev_was_caption:
                skip.add(p.id)
            continue
        if is_figure_caption_text(text):
            prev_was_caption = True
        else:
            prev_was_caption = False
    return skip


def assign_paragraph_page_numbers(paragraphs: list[ParagraphModel]) -> dict[str, int]:
    page = 1
    out: dict[str, int] = {}
    for i, p in enumerate(paragraphs):
        if i > 0 and p.starts_with_page_break:
            page += 1
        out[p.id] = page
    return out
