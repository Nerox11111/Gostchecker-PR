from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType
from engine.models.violation_model import Severity, Violation
from engine.shared.regex_patterns import FORMULA_NUMBER_RE


@dataclass
class FormulaFormatChecker:
    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.FORMULA}

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

            # 1) Выравнивание по центру.
            if p.alignment and "CENTER" not in str(p.alignment).upper():
                violations.append(
                    Violation(
                        code="FORMULA_FORMAT_INVALID",
                        element_id=p.id,
                        message="Формула должна быть выровнена по центру",
                        expected="CENTER",
                        actual=str(p.alignment),
                        zone_type=p.zone_type,
                        actual_text=p.text[:120] if p.text else None,
                        severity=Severity.MEDIUM,
                        rule_ref="gost-formula-format-center",
                    )
                )

            # 2) Нумерация формулы справа в скобках (если в видимом тексте есть номер).
            text = p.text.strip() if p.text else ""
            if text and FORMULA_NUMBER_RE.search(text) is None:
                violations.append(
                    Violation(
                        code="FORMULA_FORMAT_INVALID",
                        element_id=p.id,
                        message="В строке формулы отсутствует номер в скобках",
                        expected="(N)",
                        actual=text[:80],
                        zone_type=p.zone_type,
                        actual_text=p.text[:120] if p.text else None,
                        severity=Severity.MEDIUM,
                        rule_ref="gost-formula-numbering-brackets",
                    )
                )

        return violations

