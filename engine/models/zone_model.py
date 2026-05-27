from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ZoneType(str, Enum):
    TITLE_PAGE = "TITLE_PAGE"
    TOC = "TOC"
    MAIN_CONTENT = "MAIN_CONTENT"
    TABLE = "TABLE"
    FIGURE = "FIGURE"
    FORMULA = "FORMULA"
    LISTING = "LISTING"
    BIBLIOGRAPHY = "BIBLIOGRAPHY"
    APPENDIX = "APPENDIX"


@dataclass(frozen=True)
class Zone:
    id: str
    zone_type: ZoneType
    # На данном этапе: список element_id, которые попадают в зону.
    # Позже можно заменить на индексы/DOM-ссылки.
    element_ids: list[str]

