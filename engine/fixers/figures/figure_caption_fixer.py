from __future__ import annotations

from dataclasses import dataclass

from engine.core.fixer import BaseFixer
from engine.models.document_model import DocumentModel
from engine.models.violation_model import FixOperation, Violation
from engine.shared.figure_caption_utils import normalize_figure_caption
from engine.shared.figure_format import figure_caption_format


@dataclass
class FigureCaptionFixer:
    def supported_violation_codes(self) -> set[str]:
        return {"FIGURE_CAPTION_INVALID", "FIGURE_CAPTION_FORMAT_WRONG"}

    def build_fixes(self, document: DocumentModel, violations: list[Violation]) -> list[FixOperation]:
        ops: list[FixOperation] = []
        seen: set[str] = set()
        for v in violations:
            if v.code not in self.supported_violation_codes() or v.element_id in seen:
                continue
            seen.add(v.element_id)
            p = next((x for x in document.paragraphs if x.id == v.element_id), None)
            if not p or not p.text:
                continue
            new_text = normalize_figure_caption(p.text)
            if new_text and new_text.strip() != p.text.strip():
                ops.append(
                    FixOperation(
                        action="SET_PARAGRAPH_TEXT",
                        target_element_id=v.element_id,
                        value=new_text,
                        meta={"alignment": "CENTER"},
                    )
                )
            ops.append(
                FixOperation(
                    action="SET_PARAGRAPH_FORMAT",
                    target_element_id=v.element_id,
                    meta=figure_caption_format(),
                )
            )
        return ops
