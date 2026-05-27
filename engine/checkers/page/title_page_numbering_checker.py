from __future__ import annotations

from dataclasses import dataclass

from engine.models.violation_model import Severity, Violation
from engine.models.zone_model import ZoneType


@dataclass
class TitlePageNumberingChecker:
    """Проверяет, что номер на титульнике скрыт/исключён из нумерации."""

    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.TITLE_PAGE, ZoneType.MAIN_CONTENT}

    def run(self, document, zones) -> list:
        violations: list[Violation] = []
        for section in (document.numbering or {}).get("sections") or []:
            if section.get("first_footer_has_page_field"):
                violations.append(
                    Violation(
                        code="TITLE_PAGE_NUMBERING_INVALID",
                        element_id=f"section_{section.get('index', 0)}",
                        message="Номер страницы не должен отображаться на титульном листе",
                        expected="empty first-page footer",
                        actual="PAGE field in first-page footer",
                        severity=Severity.MEDIUM,
                        rule_ref="gost-title-page-numbering",
                    )
                )
        return violations

