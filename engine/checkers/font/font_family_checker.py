from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType
from engine.models.violation_model import Severity, Violation
from engine.shared.constants import GOST_MAIN_FONT_NAME


@dataclass
class FontFamilyChecker:
    """Проверяет базовый шрифт основного текста."""

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

            expected = GOST_MAIN_FONT_NAME
            actual_fonts = {
                (rm.get("font_name") or "").strip()
                for rm in p.runs_meta
                if (rm.get("font_name") or "").strip()
            }
            if not actual_fonts:
                continue

            # Если среди заданных есть нецелевые значения — считаем нарушением.
            if any(f != expected for f in actual_fonts):
                # Берём первое “плохое” значение для читабельности.
                bad = next(f for f in actual_fonts if f != expected)
                violations.append(
                    Violation(
                        code="FONT_FAMILY_INVALID",
                        element_id=p.id,
                        message="Некорректный шрифт основного текста",
                        expected=expected,
                        actual=bad,
                        zone_type=p.zone_type,
                        actual_text=p.text[:120] if p.text else None,
                        severity=Severity.HIGH,
                        rule_ref="gost-font-family",
                    )
                )

        return violations

