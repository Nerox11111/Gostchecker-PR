from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SectionModel:
    index: int
    orientation: str | None = None  # "portrait"/"landscape"
    page_width_mm: float | None = None
    page_height_mm: float | None = None
    margin_left_mm: float | None = None
    margin_right_mm: float | None = None
    margin_top_mm: float | None = None
    margin_bottom_mm: float | None = None

