from __future__ import annotations

from dataclasses import dataclass

from engine.models.violation_model import Severity, Violation
from engine.models.zone_model import ZoneType


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
        for p in document.paragraphs:
            if p.id not in allowed_ids:
                continue
            xml = getattr(p, "xml_element", None)
            xml_text = xml.xml if xml is not None else ""
            if "w:drawing" not in xml_text and "w:pict" not in xml_text:
                continue

            al = str(p.alignment or "").upper()
            if "CENTER" not in al and "(1)" not in al:
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

