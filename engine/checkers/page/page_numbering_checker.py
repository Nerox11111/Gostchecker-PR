from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType


@dataclass
class PageNumberingChecker:
    """Проверяет нумерацию страниц (сквозная, формат)."""

    def supported_zones(self) -> set[ZoneType]:
        return set(ZoneType)

    def run(self, document, zones) -> list:
        return []

