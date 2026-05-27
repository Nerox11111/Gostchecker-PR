from __future__ import annotations

from dataclasses import dataclass

from engine.core.fixer import BaseFixer
from engine.models.document_model import DocumentModel
from engine.models.violation_model import FixOperation, Violation
from engine.shared.figure_caption_utils import is_figure_caption_text
from engine.shared.figure_format import figure_caption_format, figure_paragraph_format


@dataclass
class FigureLayoutFixer:
    def supported_violation_codes(self) -> set[str]:
        return {"FIGURE_NOT_CENTERED", "FIGURE_INDENT_WRONG", "FIGURE_MISSING_BLANK_BEFORE"}

    def build_fixes(self, document: DocumentModel, violations: list[Violation]) -> list[FixOperation]:
        ids = {v.element_id for v in violations if v.code in self.supported_violation_codes()}
        ops: list[FixOperation] = []
        pos = {p.id: i for i, p in enumerate(document.paragraphs)}

        for pid in ids:
            idx = pos.get(pid)
            if idx is None:
                continue

            # 1) Сам абзац с рисунком: центр + нулевой отступ.
            ops.append(
                FixOperation(
                    action="SET_PARAGRAPH_FORMAT",
                    target_element_id=pid,
                    meta=figure_paragraph_format(),
                )
            )

            # 2) Строка выше: если непустая — вставляем пустую строку перед рисунком.
            if idx > 0:
                prev = document.paragraphs[idx - 1]
                if (prev.text or "").strip():
                    ops.append(
                        FixOperation(
                            action="INSERT_EMPTY_PARAGRAPH_BEFORE",
                            target_element_id=pid,
                            value="",
                            meta=figure_paragraph_format(),
                        )
                    )
                else:
                    ops.append(
                        FixOperation(
                            action="SET_PARAGRAPH_FORMAT",
                            target_element_id=prev.id,
                            meta=figure_paragraph_format(),
                        )
                    )

            # 3) Если следующая строка — подпись рисунка, выравниваем её по центру.
            if idx + 1 < len(document.paragraphs):
                nxt = document.paragraphs[idx + 1]
                if is_figure_caption_text(nxt.text or ""):
                    ops.append(
                        FixOperation(
                            action="SET_PARAGRAPH_FORMAT",
                            target_element_id=nxt.id,
                            meta=figure_caption_format(),
                        )
                    )
        return ops

