from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType
from engine.models.violation_model import Severity, Violation


@dataclass
class FontStyleChecker:
    """Проверяет начертания (bold/italic/underline) основного текста."""

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

            if any(rm.get("underline") is True for rm in p.runs_meta):
                violations.append(
                    Violation(
                        code="FONT_STYLE_INVALID",
                        element_id=p.id,
                        message="Подчёркивание в основном тексте запрещено",
                        expected="underline=False",
                        actual="underline=True",
                        zone_type=p.zone_type,
                        actual_text=p.text[:120] if p.text else None,
                        severity=Severity.MEDIUM,
                        rule_ref="gost-font-style",
                    )
                )

        return violations

