from __future__ import annotations

from dataclasses import dataclass

from engine.models.violation_model import Severity, Violation
from engine.models.zone_model import ZoneType
from engine.shared.figure_format import is_center_alignment


@dataclass
class FigureLayoutChecker:
    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.MAIN_CONTENT, ZoneType.FIGURE, ZoneType.APPENDIX}

    def run(self, document, zones) -> list:
        if not zones:
            return []
        allowed_ids: set[str] = set()
        for z in zones:
            allowed_ids.update(z.element_ids)

        violations: list[Violation] = []
        position = {p.id: i for i, p in enumerate(document.paragraphs)}

        for p in document.paragraphs:
            if p.id not in allowed_ids:
                continue
            xml = getattr(p, "xml_element", None)
            xml_text = xml.xml if xml is not None else ""
            if "w:drawing" not in xml_text and "w:pict" not in xml_text:
                continue

            if not is_center_alignment(p.alignment):
                violations.append(
                    Violation(
                        code="FIGURE_NOT_CENTERED",
                        element_id=p.id,
                        message="Рисунок не выровнен по центру",
                        expected="CENTER",
                        actual=str(p.alignment),
                        actual_text=(p.text or "")[:120],
                        severity=Severity.MEDIUM,
                        zone_type=p.zone_type,
                        rule_ref="gost-figure-alignment",
                    )
                )

            idx = position.get(p.id)
            prev = document.paragraphs[idx - 1] if idx is not None and idx > 0 else None
            prev_text = (prev.text or "").strip() if prev is not None else None
            if prev is None or prev_text or not is_center_alignment(prev.alignment):
                actual = "missing" if prev is None or prev_text else str(prev.alignment)
                violations.append(
                    Violation(
                        code="FIGURE_MISSING_BLANK_BEFORE",
                        element_id=p.id,
                        message="Перед рисунком должна быть пустая строка с выравниванием по центру",
                        expected="centered empty paragraph before figure",
                        actual=actual,
                        actual_text=(p.text or "")[:120],
                        severity=Severity.MEDIUM,
                        zone_type=p.zone_type,
                        rule_ref="gost-figure-blank-before",
                    )
                )
            if p.first_line_indent_cm is not None and abs(p.first_line_indent_cm) > 0.05:
                violations.append(
                    Violation(
                        code="FIGURE_INDENT_WRONG",
                        element_id=p.id,
                        message="Неверный отступ первой строки у абзаца с рисунком",
                        expected="0",
                        actual=str(p.first_line_indent_cm),
                        actual_text=(p.text or "")[:120],
                        severity=Severity.MEDIUM,
                        zone_type=p.zone_type,
                        rule_ref="gost-figure-indent",
                    )
                )
        return violations

