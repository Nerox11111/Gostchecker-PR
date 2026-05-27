from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType


@dataclass
class TitlePageNumberingChecker:
    """Проверяет, что номер на титульнике скрыт/исключён из нумерации."""

    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.TITLE_PAGE, ZoneType.MAIN_CONTENT}

    def run(self, document, zones) -> list:
        return []

