from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType
from engine.models.violation_model import Severity, Violation
from engine.shared.constants import (
    GOST_FIRST_LINE_INDENT_CM,
    GOST_LEFT_INDENT_CM,
    GOST_LINE_SPACING_MAIN,
    GOST_RIGHT_INDENT_CM,
    GOST_SPACE_AFTER_PT,
    GOST_SPACE_BEFORE_PT,
)
from engine.shared.figure_caption_utils import (
    build_blank_after_figure_caption_ids,
    is_figure_caption_text,
)
from engine.shared.figure_format import has_figure_image
from engine.shared.paragraph_roles import is_structural_heading, is_zero_indent_exception


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
            if has_figure_image(getattr(p, "xml_element", None)):
                continue
            if is_figure_caption_text(p.text or ""):
                continue
            if p.id in skip_blank_ids:
                continue

            text = (p.text or "").strip()
            if not text:
                continue
            if is_structural_heading(text):
                continue

            issues: list[str] = []
            if p.line_spacing is None or abs(p.line_spacing - GOST_LINE_SPACING_MAIN) > 0.1:
                issues.append(f"line_spacing={p.line_spacing}")
            if not is_zero_indent_exception(text):
                if p.first_line_indent_cm is None or abs(p.first_line_indent_cm - GOST_FIRST_LINE_INDENT_CM) > 0.15:
                    issues.append(f"first_indent_cm={p.first_line_indent_cm}")
            if p.left_indent_cm is not None and abs(p.left_indent_cm - GOST_LEFT_INDENT_CM) > 0.05:
                issues.append(f"left_indent_cm={p.left_indent_cm}")
            if p.right_indent_cm is not None and abs(p.right_indent_cm - GOST_RIGHT_INDENT_CM) > 0.05:
                issues.append(f"right_indent_cm={p.right_indent_cm}")
            if p.space_before_pt is not None and abs(p.space_before_pt - GOST_SPACE_BEFORE_PT) > 0.5:
                issues.append(f"space_before_pt={p.space_before_pt}")
            if p.space_after_pt is not None and abs(p.space_after_pt - GOST_SPACE_AFTER_PT) > 0.5:
                issues.append(f"space_after_pt={p.space_after_pt}")

            al = str(p.alignment or "").upper()
            if "JUSTIFY" not in al and "(3)" not in al:
                issues.append(f"alignment={p.alignment}")

            if issues:
                violations.append(
                    Violation(
                        code="FONT_SPACING_INVALID",
                        element_id=p.id,
                        message="Некорректные параметры интервалов/отступов",
                        expected="line_spacing=1.5, first_indent=1.25cm, left/right indent=0cm, space_before/after=0pt, alignment=justify",
                        actual=";".join(issues),
                        zone_type=p.zone_type,
                        actual_text=p.text[:120] if p.text else None,
                        severity=Severity.MEDIUM,
                        rule_ref="gost-font-spacing",
                    )
                )

        return violations
