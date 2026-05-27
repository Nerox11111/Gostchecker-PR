from __future__ import annotations

from dataclasses import dataclass

from engine.core.fixer import BaseFixer
from engine.models.document_model import DocumentModel
from engine.models.violation_model import FixOperation, Violation
from engine.shared.figure_caption_utils import is_figure_caption_text, normalize_figure_caption
from engine.shared.figure_format import figure_caption_format, figure_paragraph_format, has_figure_image


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
            if not has_figure_image(getattr(p, "xml_element", None)):
                continue

            # Пустая строка сверху, если предыдущий абзац не пустой.
            if i > 0:
                prev = paragraphs[i - 1]
                if (prev.text or "").strip():
                    ops.append(
                        FixOperation(
                            action="INSERT_EMPTY_PARAGRAPH_BEFORE",
                            target_element_id=p.id,
                            meta=figure_paragraph_format(),
                        )
                    )

            ops.append(
                FixOperation(
                    action="SET_PARAGRAPH_FORMAT",
                    target_element_id=p.id,
                    meta=figure_paragraph_format(),
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
                            meta=figure_caption_format(),
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
                    meta=figure_caption_format(),
                )
            )

        return ops
