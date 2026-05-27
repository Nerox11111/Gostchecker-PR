from __future__ import annotations

from dataclasses import dataclass
import re

from engine.models.zone_model import ZoneType
from engine.models.violation_model import Severity, Violation
from engine.shared.constants import (
    GOST_MAIN_FONT_NAME,
    GOST_MAIN_FONT_SIZE_PT,
    GOST_LISTING_FONT_SIZE_PT_MAX,
    GOST_LISTING_FONT_SIZE_PT_MIN,
    GOST_LISTING_INDENT_CM,
)
from engine.shared.regex_patterns import LISTING_CAPTION_RE
from engine.shared.constants import GOST_LISTING_LINE_SPACING


@dataclass
class ListingFormatChecker:
    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.LISTING}

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
                # Листинги в таблицах можно будет обработать отдельной логикой,
                # пока пропускаем, чтобы снизить ложные срабатывания.
                continue
            if not p.text.strip():
                continue

            # Подпись "Листинг N — ..." проверяем отдельно как обычный текст подписи.
            if LISTING_CAPTION_RE.match(p.text.strip()):
                text = p.text.strip()
                if "—" not in text:
                    violations.append(
                        Violation(
                            code="LISTING_CAPTION_FONT",
                            element_id=p.id,
                            message="Подпись листинга должна использовать длинное тире",
                            expected="Листинг N — Наименование",
                            actual=text,
                            zone_type=p.zone_type,
                            actual_text=text[:120],
                            severity=Severity.MEDIUM,
                            rule_ref="gost-listing-caption-dash",
                        )
                    )
                if p.alignment and "LEFT" not in str(p.alignment).upper():
                    violations.append(
                        Violation(
                            code="LISTING_CAPTION_FONT",
                            element_id=p.id,
                            message="Подпись листинга выравнивается по левому краю",
                            expected="LEFT",
                            actual=str(p.alignment),
                            zone_type=p.zone_type,
                            actual_text=text[:120],
                            severity=Severity.MEDIUM,
                            rule_ref="gost-listing-caption-align",
                        )
                    )
                continue

            issues: list[str] = []

            # Шрифт Courier New / Consolas.
            font_names = {
                (rm.get("font_name") or "").lower()
                for rm in p.runs_meta
                if (rm.get("font_name") or "").strip()
            }
            if font_names:
                if not any("courier" in n or "consolas" in n for n in font_names):
                    issues.append(f"font={sorted(font_names)[:3]}")

            # Размер шрифта 10-12 pt.
            sizes = [rm.get("font_size_pt") for rm in p.runs_meta if rm.get("font_size_pt") is not None]
            if sizes:
                size = min(sizes)
                if size < GOST_LISTING_FONT_SIZE_PT_MIN or size > GOST_LISTING_FONT_SIZE_PT_MAX:
                    issues.append(f"font_size={size}")

            # Интервал (в реализациях правок используется 1.15).
            if p.line_spacing is not None and abs(p.line_spacing - GOST_LISTING_LINE_SPACING) > 0.15:
                issues.append(f"line_spacing={p.line_spacing}")

            # Абзацный отступ 2 см.
            if p.first_line_indent_cm is not None and abs(p.first_line_indent_cm - GOST_LISTING_INDENT_CM) > 0.3:
                issues.append(f"indent_cm={p.first_line_indent_cm}")

            # Выравнивание по левому краю.
            if p.alignment and "LEFT" not in str(p.alignment).upper():
                issues.append(f"alignment={p.alignment}")

            if issues:
                violations.append(
                    Violation(
                            code="LISTING_CODE_FONT",
                        element_id=p.id,
                        message="Некорректное форматирование листинга",
                        expected="Courier New, 10-12pt, line_spacing~1.15, indent=2cm, LEFT",
                        actual=";".join(issues),
                        zone_type=p.zone_type,
                        actual_text=p.text[:120] if p.text else None,
                        severity=Severity.MEDIUM,
                        rule_ref="gost-listing-format",
                    )
                )

        return violations

