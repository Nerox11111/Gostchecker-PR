from __future__ import annotations

from dataclasses import dataclass
import re

from engine.core.fixer import BaseFixer
from engine.models.document_model import DocumentModel
from engine.models.zone_model import ZoneType
from engine.models.violation_model import FixOperation, Violation
from engine.shared.constants import (
    GOST_MAIN_FONT_NAME,
    GOST_MAIN_FONT_SIZE_PT,
    GOST_LINE_SPACING_MAIN,
    GOST_FIRST_LINE_INDENT_CM,
    GOST_LISTING_FONT_SIZE_PT_MIN,
    GOST_LISTING_FONT_SIZE_PT_MAX,
    GOST_LISTING_LINE_SPACING,
    GOST_LISTING_INDENT_CM,
    GOST_MONO_FONT_NAME,
)
from engine.shared.paragraph_roles import is_listing_caption, is_structural_heading, is_zero_indent_exception


@dataclass
class FontFormatFixer:
    """Приводит шрифт/интервалы к целевым значениям."""

    def supported_violation_codes(self) -> set[str]:
        return {
            "FONT_FAMILY_INVALID",
            "FONT_SIZE_INVALID",
            "FONT_STYLE_INVALID",
            "FONT_SPACING_INVALID",
            "LISTING_CODE_FONT",
            "LISTING_CAPTION_FONT",
        }

    def build_fixes(self, document: DocumentModel, violations: list[Violation]) -> list[FixOperation]:
        if not violations:
            return []

        listing_ids = [p.id for p in document.paragraphs if p.zone_type == ZoneType.LISTING]
        heading_ids = [p.id for p in document.paragraphs if is_structural_heading(p.text or "")]
        zero_indent_ids = [p.id for p in document.paragraphs if is_zero_indent_exception(p.text or "")]
        listing_caption_ids = [p.id for p in document.paragraphs if is_listing_caption(p.text or "")]
        skip_ids = [
            p.id
            for p in document.paragraphs
            if p.zone_type in {ZoneType.TITLE_PAGE, ZoneType.FIGURE, ZoneType.TOC} or p.id in heading_ids
        ]

        # Для listing-ов выбираем “нижнюю границу” допустимого диапазона (10pt),
        # чтобы обеспечить совпадение с требованиями и не выходить за верхнюю границу.
        ops = [
            FixOperation(
                action="SET_FONT_FORMATTING",
                target_element_id=None,
                value=None,
                meta={
                    "main": {
                        "font_name": GOST_MAIN_FONT_NAME,
                        "font_size_pt": GOST_MAIN_FONT_SIZE_PT,
                        "line_spacing": GOST_LINE_SPACING_MAIN,
                        "first_line_indent_cm": GOST_FIRST_LINE_INDENT_CM,
                        "alignment": "JUSTIFY",
                    },
                    "listing": {
                        "font_name": GOST_MONO_FONT_NAME,
                        "font_size_pt": GOST_LISTING_FONT_SIZE_PT_MIN,
                        "line_spacing": GOST_LISTING_LINE_SPACING,
                        "first_line_indent_cm": GOST_LISTING_INDENT_CM,
                        "alignment": "LEFT",
                    },
                    "listing_element_ids": listing_ids,
                    "skip_element_ids": skip_ids,
                },
            )
        ]

        # Заголовки: левый край, полужирный, без точки в конце.
        for p in document.paragraphs:
            if p.id not in heading_ids:
                continue
            text = (p.text or "").strip()
            normalized = re.sub(r"^(\d+(\.\d+)*)\.\s+", r"\1 ", text)
            normalized = normalized.rstrip(".")
            if normalized != text:
                ops.append(
                    FixOperation(
                        action="SET_PARAGRAPH_TEXT",
                        target_element_id=p.id,
                        value=normalized,
                        meta={"alignment": "LEFT"},
                    )
                )
            ops.append(
                FixOperation(
                    action="SET_PARAGRAPH_FORMAT",
                    target_element_id=p.id,
                    meta={
                        "alignment": "LEFT",
                        "first_line_indent_cm": GOST_FIRST_LINE_INDENT_CM,
                        "line_spacing": GOST_LINE_SPACING_MAIN,
                        "font_name": GOST_MAIN_FONT_NAME,
                        "font_size_pt": GOST_MAIN_FONT_SIZE_PT,
                        "bold": True,
                        "italic": False,
                        "underline": False,
                    },
                )
            )

        # Исключения без отступа.
        for pid in zero_indent_ids:
            ops.append(
                FixOperation(
                    action="SET_PARAGRAPH_FORMAT",
                    target_element_id=pid,
                    meta={"first_line_indent_cm": 0.0},
                )
            )

        # Подписи листинга оформляем как обычный текст, а не код.
        for pid in listing_caption_ids:
            p = next((x for x in document.paragraphs if x.id == pid), None)
            txt = (p.text or "").strip() if p else ""
            if txt:
                normalized_caption = re.sub(r"^(Листинг\s+\d+)\s*[-–]\s*", r"\1 — ", txt, flags=re.IGNORECASE)
                if normalized_caption != txt:
                    ops.append(
                        FixOperation(
                            action="SET_PARAGRAPH_TEXT",
                            target_element_id=pid,
                            value=normalized_caption,
                            meta={"alignment": "LEFT"},
                        )
                    )
            ops.append(
                FixOperation(
                    action="SET_PARAGRAPH_FORMAT",
                    target_element_id=pid,
                    meta={
                        "alignment": "LEFT",
                        "first_line_indent_cm": 0.0,
                        "line_spacing": GOST_LINE_SPACING_MAIN,
                        "font_name": GOST_MAIN_FONT_NAME,
                        "font_size_pt": GOST_MAIN_FONT_SIZE_PT,
                        "bold": False,
                        "italic": False,
                        "underline": False,
                    },
                )
            )
        return ops

