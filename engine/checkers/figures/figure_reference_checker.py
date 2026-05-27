from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType


@dataclass
class FigureReferenceChecker:
    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.FIGURE, ZoneType.MAIN_CONTENT}

    def run(self, document, zones) -> list:
        return []

