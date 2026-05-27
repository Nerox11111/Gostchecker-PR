from __future__ import annotations

import re
from dataclasses import dataclass

from engine.models.violation_model import Severity, Violation
from engine.models.zone_model import ZoneType
from engine.shared.constants import GOST_FIRST_LINE_INDENT_CM


BULLET_PREFIX_RE = re.compile(r"^\s*([•·–\-\*→▪◦])\s+")
NUMBERED_PREFIX_RE = re.compile(r"^\s*(\d+)[\.\)]\s+")


@dataclass
class ListMarkerChecker:
    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.MAIN_CONTENT, ZoneType.APPENDIX, ZoneType.BIBLIOGRAPHY}

    def run(self, document, zones) -> list:
        if not zones:
            return []

        allowed_ids: set[str] = set()
        for z in zones:
            allowed_ids.update(z.element_ids)

        violations: list[Violation] = []
        numbered_block: list[tuple[str, int]] = []

        def flush_block() -> None:
            nonlocal numbered_block
            if len(numbered_block) < 2:
                numbered_block = []
                return
            expected = 1
            for element_id, num in numbered_block:
                if num != expected:
                    violations.append(
                        Violation(
                            code="LIST_NUMBERING_ORDER",
                            element_id=element_id,
                            message="Нарушен порядок нумерации в списке",
                            expected=f"{expected}",
                            actual=f"{num}",
                            severity=Severity.MEDIUM,
                            rule_ref="gost-list-numbering-order",
                        )
                    )
                expected += 1
            numbered_block = []

        for p in document.paragraphs:
            if p.id not in allowed_ids or getattr(p, "in_table", False):
                flush_block()
                continue
            text = (p.text or "").strip()
            if not text:
                flush_block()
                continue

            m_bullet = BULLET_PREFIX_RE.match(text)
            if m_bullet:
                symbol = m_bullet.group(1)
                if symbol != "—":
                    violations.append(
                        Violation(
                            code="LIST_MARKER_WRONG",
                            element_id=p.id,
                            message="Неверный маркер ненумерованного списка",
                            expected="—",
                            actual=symbol,
                            actual_text=text[:120],
                            zone_type=p.zone_type,
                            severity=Severity.MEDIUM,
                            rule_ref="gost-list-marker",
                        )
                    )
                if p.first_line_indent_cm is None or abs(p.first_line_indent_cm - GOST_FIRST_LINE_INDENT_CM) > 0.2:
                    violations.append(
                        Violation(
                            code="LIST_MARKER_WRONG",
                            element_id=p.id,
                            message="Неверный отступ строки списка",
                            expected=str(GOST_FIRST_LINE_INDENT_CM),
                            actual=str(p.first_line_indent_cm),
                            actual_text=text[:120],
                            zone_type=p.zone_type,
                            severity=Severity.MEDIUM,
                            rule_ref="gost-list-indent",
                        )
                    )
                flush_block()
                continue

            m_num = NUMBERED_PREFIX_RE.match(text)
            if m_num:
                numbered_block.append((p.id, int(m_num.group(1))))
                continue

            flush_block()

        flush_block()
        return violations
