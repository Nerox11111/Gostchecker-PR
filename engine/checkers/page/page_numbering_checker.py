from __future__ import annotations

from dataclasses import dataclass

from engine.models.violation_model import Severity, Violation
from engine.models.zone_model import ZoneType


@dataclass
class PageNumberingChecker:
    """Проверяет нумерацию страниц (сквозная, формат)."""

    def supported_zones(self) -> set[ZoneType]:
        return set(ZoneType)

    def run(self, document, zones) -> list:
        sections = (document.numbering or {}).get("sections") or []
        if not sections:
            return [
                Violation(
                    code="PAGE_NUMBERING_INVALID",
                    element_id="document",
                    message="Не удалось определить нумерацию страниц",
                    expected="PAGE field in centered footer",
                    actual="missing",
                    severity=Severity.MEDIUM,
                    rule_ref="gost-page-numbering-footer",
                )
            ]

        violations: list[Violation] = []
        for section in sections:
            if not section.get("footer_has_page_field"):
                violations.append(
                    Violation(
                        code="PAGE_NUMBERING_INVALID",
                        element_id=f"section_{section.get('index', 0)}",
                        message="Номер страницы отсутствует в нижнем колонтитуле",
                        expected="PAGE field in centered footer",
                        actual="missing",
                        severity=Severity.MEDIUM,
                        rule_ref="gost-page-numbering-footer",
                    )
                )
        return violations

