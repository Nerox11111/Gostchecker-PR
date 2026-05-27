from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType


@dataclass
class ListingModel:
    id: str
    zone_type: ZoneType | None = None
    page_number: int | None = None
    xml_ref: str | None = None

    caption_paragraph_id: str | None = None
    code_container_paragraph_id: str | None = None
    code_container_table_id: str | None = None

