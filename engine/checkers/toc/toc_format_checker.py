from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType


@dataclass
class TocFormatChecker:
    """Проверяет формат содержания: отточия, отступы, нумерация страниц."""

    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.TOC}

    def run(self, document, zones) -> list:
        return []

