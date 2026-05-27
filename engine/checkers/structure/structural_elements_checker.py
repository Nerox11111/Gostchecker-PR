from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType
from engine.models.violation_model import Severity, Violation
from engine.shared.constants import GOST_REQUIRED_SECTIONS


@dataclass
class StructuralElementsChecker:
    """Проверяет наличие обязательных структурных элементов."""

    def supported_zones(self) -> set[ZoneType]:
        return set(ZoneType)

    def run(self, document, zones) -> list:
        if not zones:
            return []

        allowed_ids: set[str] = set()
        for z in zones:
            allowed_ids.update(z.element_ids)

        texts = {
            p.text.strip().upper(): p.id
            for p in document.paragraphs
            if p.id in allowed_ids and p.text.strip()
        }

        violations: list[Violation] = []
        for required in GOST_REQUIRED_SECTIONS:
            req_upper = required.upper()
            if req_upper not in texts:
                violations.append(
                    Violation(
                        code="STRUCTURAL_ELEMENT_MISSING",
                        element_id=f"section:{req_upper}",
                        message="Отсутствует обязательный раздел",
                        expected=required,
                        actual=None,
                        zone_type=None,
                        actual_text=None,
                        severity=Severity.HIGH,
                        rule_ref="gost-structure-elements",
                    )
                )

        return violations

