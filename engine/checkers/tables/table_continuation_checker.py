from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType


@dataclass
class TableContinuationChecker:
    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.TABLE}

    def run(self, document, zones) -> list:
        return []

