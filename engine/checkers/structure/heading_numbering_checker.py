from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType


@dataclass
class HeadingNumberingChecker:
    """Проверяет нумерацию разделов и подразделов (1, 1.1, 1.2...)."""

    def supported_zones(self) -> set[ZoneType]:
        return set(ZoneType)

    def run(self, document, zones) -> list:
        return []

