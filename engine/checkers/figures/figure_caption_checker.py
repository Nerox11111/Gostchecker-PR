from __future__ import annotations

from dataclasses import dataclass

from engine.models.zone_model import ZoneType
from engine.models.violation_model import Severity, Violation
from engine.shared.figure_caption_utils import is_figure_caption_text, is_valid_gost_figure_caption


@dataclass
class FigureCaptionChecker:
    """Проверяет формат подписи рисунка по ГОСТ."""

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

            if is_valid_gost_figure_caption(text):
                continue

            expected = "Рисунок N — Наименование (без точки в конце, тире — длинное)"
            violations.append(
                Violation(
                    code="FIGURE_CAPTION_INVALID",
                    element_id=p.id,
                    message="Неверное оформление подписи рисунка",
                    expected=expected,
                    actual=text,
                    zone_type=p.zone_type,
                    actual_text=text[:120],
                    severity=Severity.HIGH,
                    rule_ref="gost-figure-caption-format",
                )
            )

        return violations
