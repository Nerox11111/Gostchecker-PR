from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType


@dataclass
class AbbrevUsageChecker:
    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.MAIN_CONTENT, ZoneType.APPENDIX}

    def run(self, document, zones) -> list:
        return []

