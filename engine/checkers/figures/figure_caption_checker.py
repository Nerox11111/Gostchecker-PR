from __future__ import annotations

from dataclasses import dataclass

from engine.models.violation_model import Severity, Violation
from engine.models.zone_model import ZoneType
from engine.shared.figure_caption_utils import is_figure_caption_text, is_valid_gost_figure_caption
from engine.shared.figure_format import is_center_alignment


@dataclass
class FigureCaptionChecker:
    """Проверяет текст и форматирование подписи рисунка по ГОСТ."""

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
            if getattr(p, "in_table", False):
                continue

            text = (p.text or "").strip()
            if not text:
                continue
            if not is_figure_caption_text(text):
                continue

            if not is_valid_gost_figure_caption(text):
                violations.append(
                    Violation(
                        code="FIGURE_CAPTION_INVALID",
                        element_id=p.id,
                        message="Неверное оформление подписи рисунка",
                        expected="Рисунок N — Наименование (без точки в конце)",
                        actual=text,
                        zone_type=p.zone_type,
                        actual_text=text[:120],
                        severity=Severity.HIGH,
                        rule_ref="gost-figure-caption-format",
                    )
                )

            issues: list[str] = []
            if not is_center_alignment(p.alignment):
                issues.append(f"alignment={p.alignment}")
            if p.first_line_indent_cm is not None and abs(p.first_line_indent_cm) > 0.05:
                issues.append(f"first_indent_cm={p.first_line_indent_cm}")
            if p.line_spacing is not None and abs(p.line_spacing - 1.5) > 0.1:
                issues.append(f"line_spacing={p.line_spacing}")

            if issues:
                violations.append(
                    Violation(
                        code="FIGURE_CAPTION_FORMAT_WRONG",
                        element_id=p.id,
                        message="Неверное форматирование подписи рисунка",
                        expected="выравнивание по центру, отступ первой строки 0 см, интервал 1.5",
                        actual=";".join(issues),
                        zone_type=p.zone_type,
                        actual_text=text[:120],
                        severity=Severity.MEDIUM,
                        rule_ref="gost-figure-caption-paragraph-format",
                    )
                )

        return violations
