from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType


@dataclass
class FormulaModel:
    id: str
    zone_type: ZoneType | None = None
    paragraph_id: str | None = None
    page_number: int | None = None
    xml_ref: str | None = None

    numbering_value: str | None = None
    has_where_block: bool | None = None

