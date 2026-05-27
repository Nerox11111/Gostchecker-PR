from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType


@dataclass
class TableReferenceChecker:
    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.TABLE, ZoneType.MAIN_CONTENT}

    def run(self, document, zones) -> list:
        return []

