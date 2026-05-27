from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType
from engine.models.violation_model import Violation, Severity
from engine.shared.constants import (
    GOST_PAGE_MARGINS_LANDSCAPE_MM,
    GOST_PAGE_MARGINS_PORTRAIT_MM,
)


@dataclass
class MarginsChecker:
    """Проверяет размеры полей страницы."""

    def supported_zones(self) -> set[ZoneType]:
        return set(ZoneType)

    def run(self, document, zones) -> list:
        if not document.sections:
            return [
                Violation(
                    code="PAGE_SETTINGS_MISSING",
                    element_id="section_0",
                    message="Не удалось извлечь настройки секций из DOCX",
                    expected=None,
                    actual=None,
                    zone_type=None,
                    severity=Severity.HIGH,
                )
            ]

        sec = document.sections[0]
        orientation = (sec.orientation or "").upper()
        expected = (
            GOST_PAGE_MARGINS_LANDSCAPE_MM if "LANDSCAPE" in orientation else GOST_PAGE_MARGINS_PORTRAIT_MM
        )
        actual = {
            "top": sec.margin_top_mm,
            "bottom": sec.margin_bottom_mm,
            "left": sec.margin_left_mm,
            "right": sec.margin_right_mm,
        }

        tolerance = 0.2
        violations: list[Violation] = []

        def in_range(val: float | None, exp: float) -> bool:
            if val is None:
                return False
            return (exp - tolerance) <= val <= (exp + tolerance)

        for key in ("top", "bottom", "left", "right"):
            if not in_range(actual.get(key), expected[key]):
                violations.append(
                    Violation(
                        code="PAGE_MARGINS_INVALID",
                        element_id="section_0",
                        message=f"Некорректные поля: {key}",
                        expected=str(expected[key]),
                        actual=str(actual.get(key)),
                        zone_type=None,
                        severity=Severity.HIGH,
                        rule_ref="gost-page-margins",
                    )
                )

        return violations

