from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from engine.models.zone_model import ZoneType


@dataclass
class TableModel:
    id: str
    zone_type: ZoneType | None = None
    page_number: int | None = None
    xml_ref: str | None = None

    caption_paragraph_id: str | None = None
    continuation_of_table_id: str | None = None

    # Технические размеры
    rows: int | None = None
    cols: int | None = None

    meta: dict[str, Any] = field(default_factory=dict)

