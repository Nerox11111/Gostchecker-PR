from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from engine.models.zone_model import ZoneType


@dataclass
class ParagraphModel:
    id: str
    text: str
    style_name: str | None = None
    page_number: int | None = None
    section_index: int | None = None
    zone_type: ZoneType | None = None
    xml_ref: str | None = None

    # Сырые XML-данные параграфа (используются эвристиками для OMML/PageBreak).
    # На экспорт/сериализацию не рассчитано.
    xml_element: Any | None = None

    # Был ли разрыв страницы “в начале” параграфа.
    starts_with_page_break: bool = False

    alignment: str | None = None
    line_spacing: float | None = None
    first_line_indent_cm: float | None = None
    left_indent_cm: float | None = None
    right_indent_cm: float | None = None
    space_before_pt: float | None = None
    space_after_pt: float | None = None
    in_table: bool = False
    in_header_footer: bool = False

    # Метаданные по runs: шрифты/размеры/жирный/курсив/подчёркивание и т.п.
    runs_meta: list[dict[str, Any]] = field(default_factory=list)

