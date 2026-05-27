from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType
from engine.models.violation_model import Severity, Violation
from engine.shared.constants import GOST_MAIN_FONT_SIZE_PT, GOST_MIN_FONT_SIZE_PT


@dataclass
class FontSizeChecker:
    """Проверяет размер шрифта основного текста."""

    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.MAIN_CONTENT}

    def run(self, document, zones) -> list:
        if not zones:
            return []

        allowed_ids: set[str] = set()
        for z in zones:
            allowed_ids.update(z.element_ids)

        violations: list[Violation] = []
        for p in document.paragraphs:
            if p.id not in allowed_ids:
                continue
            if getattr(p, "in_table", False):
                continue

            sizes = [rm.get("font_size_pt") for rm in p.runs_meta if rm.get("font_size_pt") is not None]
            if not sizes:
                continue

            actual = min(sizes)
            if actual < GOST_MIN_FONT_SIZE_PT:
                violations.append(
                    Violation(
                        code="FONT_SIZE_INVALID",
                        element_id=p.id,
                        message="Шрифт основного текста меньше допустимого",
                        expected=f">={GOST_MIN_FONT_SIZE_PT}",
                        actual=str(actual),
                        zone_type=p.zone_type,
                        actual_text=p.text[:120] if p.text else None,
                        severity=Severity.HIGH,
                        rule_ref="gost-font-size",
                    )
                )
            else:
                # Проверяем “целевой” размер (допуск).
                tolerance = 0.5
                if abs(actual - GOST_MAIN_FONT_SIZE_PT) > tolerance:
                    violations.append(
                        Violation(
                            code="FONT_SIZE_INVALID",
                            element_id=p.id,
                            message="Шрифт основного текста отличается от целевого",
                            expected=str(GOST_MAIN_FONT_SIZE_PT),
                            actual=str(actual),
                            zone_type=p.zone_type,
                            actual_text=p.text[:120] if p.text else None,
                            severity=Severity.MEDIUM,
                            rule_ref="gost-font-size",
                        )
                    )

        return violations

