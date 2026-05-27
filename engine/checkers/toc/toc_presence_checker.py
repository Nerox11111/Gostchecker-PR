from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType


@dataclass
class TocPresenceChecker:
    """Проверяет наличие содержания и обязательных подразделов."""

    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.TOC}

    def run(self, document, zones) -> list:
        return []

