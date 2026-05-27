from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType
from engine.models.violation_model import Severity, Violation
from engine.shared.constants import GOST_FIRST_LINE_INDENT_CM, GOST_LINE_SPACING_MAIN
from engine.shared.figure_caption_utils import (
    build_blank_after_figure_caption_ids,
    is_figure_caption_text,
)
from engine.shared.paragraph_roles import is_zero_indent_exception


@dataclass
class FontSpacingChecker:
    """Проверяет межстрочный интервал и абзацные отступы основного текста."""

    def supported_zones(self) -> set[ZoneType]:
        return {ZoneType.MAIN_CONTENT}

    def run(self, document, zones) -> list:
        if not zones:
            return []

        allowed_ids: set[str] = set()
        for z in zones:
            allowed_ids.update(z.element_ids)

        skip_blank_ids = build_blank_after_figure_caption_ids(document.paragraphs)

        violations: list[Violation] = []
        for p in document.paragraphs:
            if p.id not in allowed_ids:
                continue
            if getattr(p, "in_table", False):
                continue
            if p.zone_type == ZoneType.TITLE_PAGE:
                continue
            if p.zone_type == ZoneType.FIGURE:
                continue
            if is_figure_caption_text(p.text or ""):
                continue
            if p.id in skip_blank_ids:
                continue

            text = (p.text or "").strip()
            if not text:
                continue

            issues: list[str] = []
            if p.line_spacing is not None and abs(p.line_spacing - GOST_LINE_SPACING_MAIN) > 0.1:
                issues.append(f"line_spacing={p.line_spacing}")
            if p.first_line_indent_cm is not None and abs(p.first_line_indent_cm - GOST_FIRST_LINE_INDENT_CM) > 0.15:
                if not is_zero_indent_exception(text):
                    issues.append(f"first_indent_cm={p.first_line_indent_cm}")

            if p.alignment:
                al = str(p.alignment).upper()
                if "JUSTIFY" not in al and "(3)" not in al:
                    issues.append(f"alignment={p.alignment}")

            if issues:
                violations.append(
                    Violation(
                        code="FONT_SPACING_INVALID",
                        element_id=p.id,
                        message="Некорректные параметры интервалов/отступов",
                        expected="line_spacing=1.5, first_indent=1.25cm, alignment=justify",
                        actual=";".join(issues),
                        zone_type=p.zone_type,
                        actual_text=p.text[:120] if p.text else None,
                        severity=Severity.MEDIUM,
                        rule_ref="gost-font-spacing",
                    )
                )

        return violations
