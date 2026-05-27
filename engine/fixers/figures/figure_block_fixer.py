from __future__ import annotations

from dataclasses import dataclass

from engine.core.fixer import BaseFixer
from engine.models.document_model import DocumentModel
from engine.models.violation_model import FixOperation, Violation
from engine.shared.constants import (
    GOST_FIRST_LINE_INDENT_CM,
    GOST_LINE_SPACING_MAIN,
    GOST_MAIN_FONT_NAME,
    GOST_MAIN_FONT_SIZE_PT,
)
from engine.shared.figure_caption_utils import is_figure_caption_text, normalize_figure_caption


def _has_image(xml_element) -> bool:
    if xml_element is None:
        return False
    xml = xml_element.xml if hasattr(xml_element, "xml") else ""
    return "w:drawing" in xml or "w:pict" in xml or "w:drawing" in str(xml)


@dataclass
class FigureBlockFixer:
    """Центрирует рисунок, подпись и добавляет пустую строку сверху при необходимости."""

    def supported_violation_codes(self) -> set[str]:
        return {
            "FIGURE_NOT_CENTERED",
            "FIGURE_INDENT_WRONG",
            "FIGURE_CAPTION_INVALID",
        }

    def build_fixes(self, document: DocumentModel, violations: list[Violation]) -> list[FixOperation]:
        ops: list[FixOperation] = []
        paragraphs = document.paragraphs
        n = len(paragraphs)

        for i, p in enumerate(paragraphs):
            if not _has_image(getattr(p, "xml_element", None)):
                continue

            # Пустая строка сверху, если предыдущий абзац не пустой.
            if i > 0:
                prev = paragraphs[i - 1]
                if (prev.text or "").strip():
                    ops.append(
                        FixOperation(
                            action="INSERT_EMPTY_PARAGRAPH_BEFORE",
                            target_element_id=p.id,
                        )
                    )

            ops.append(
                FixOperation(
                    action="SET_PARAGRAPH_FORMAT",
                    target_element_id=p.id,
                    meta={"alignment": "CENTER", "first_line_indent_cm": 0.0},
                )
            )

            # Подпись обычно сразу под рисунком.
            if i + 1 < n:
                nxt = paragraphs[i + 1]
                if is_figure_caption_text(nxt.text or ""):
                    caption_text = normalize_figure_caption(nxt.text or "") or (nxt.text or "").strip()
                    ops.append(
                        FixOperation(
                            action="SET_PARAGRAPH_TEXT",
                            target_element_id=nxt.id,
                            value=caption_text,
                            meta={"alignment": "CENTER"},
                        )
                    )
                    ops.append(
                        FixOperation(
                            action="SET_PARAGRAPH_FORMAT",
                            target_element_id=nxt.id,
                            meta={
                                "alignment": "CENTER",
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

        # Подписи без рисунка непосредственно выше (отдельные абзацы).
        for p in paragraphs:
            if not is_figure_caption_text(p.text or ""):
                continue
            if any(op.target_element_id == p.id and op.action == "SET_PARAGRAPH_FORMAT" for op in ops):
                continue
            caption_text = normalize_figure_caption(p.text or "") or (p.text or "").strip()
            ops.append(
                FixOperation(
                    action="SET_PARAGRAPH_TEXT",
                    target_element_id=p.id,
                    value=caption_text,
                    meta={"alignment": "CENTER"},
                )
            )
            ops.append(
                FixOperation(
                    action="SET_PARAGRAPH_FORMAT",
                    target_element_id=p.id,
                    meta={
                        "alignment": "CENTER",
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
