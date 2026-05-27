from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType
from engine.models.violation_model import Severity, Violation

import re


@dataclass
class TableCaptionChecker:
    def supported_zones(self) -> set[ZoneType]:
        # Подписи обычно в основном тексте, не в “таблицах” как объектах DOCX.
        return {ZoneType.MAIN_CONTENT, ZoneType.BIBLIOGRAPHY, ZoneType.APPENDIX}

    def run(self, document, zones) -> list:
        if not zones:
            return []

        allowed_ids: set[str] = set()
        for z in zones:
            allowed_ids.update(z.element_ids)

        TABLE_CAPTION_RE = re.compile(r"^Таблица\s+\d+\s+[–—]\s+.+$", re.IGNORECASE)

        violations: list[Violation] = []
        for p in document.paragraphs:
            if p.id not in allowed_ids:
                continue
            if not p.text.strip():
                continue

            if not re.match(r"^Таблица\s+\d+", p.text.strip(), re.IGNORECASE):
                continue

            text = p.text.strip()
            if not TABLE_CAPTION_RE.match(text) or text.endswith("."):
                # Попытка сформировать expected/actual для человека.
                expected = "Таблица N — Наименование (без точки в конце)"
                actual = text
                violations.append(
                    Violation(
                        code="TABLE_CAPTION_INVALID",
                        element_id=p.id,
                        message="Некорректный формат подписи таблицы",
                        expected=expected,
                        actual=actual,
                        zone_type=p.zone_type,
                        actual_text=p.text[:120] if p.text else None,
                        severity=Severity.HIGH,
                        rule_ref="gost-table-caption-format",
                    )
                )
                continue

            # Выравнивание по левому краю (упрощённо).
            if p.alignment and "LEFT" not in str(p.alignment).upper():
                violations.append(
                    Violation(
                        code="TABLE_CAPTION_INVALID",
                        element_id=p.id,
                        message="Подпись таблицы должна быть выровнена по левому краю",
                        expected="LEFT",
                        actual=str(p.alignment),
                        zone_type=p.zone_type,
                        actual_text=p.text[:120] if p.text else None,
                        severity=Severity.MEDIUM,
                        rule_ref="gost-table-caption-alignment",
                    )
                )

        return violations

