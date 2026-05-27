from __future__ import annotations

from dataclasses import dataclass

from engine.core.fixer import BaseFixer
from engine.models.document_model import DocumentModel
from engine.models.violation_model import FixOperation, Violation


@dataclass
class PageNumberingFixer:
    """Исправляет формат/сквозную нумерацию страниц."""

    def supported_violation_codes(self) -> set[str]:
        return {"PAGE_NUMBERING_INVALID", "TITLE_PAGE_NUMBERING_INVALID"}

    def build_fixes(self, document: DocumentModel, violations: list[Violation]) -> list[FixOperation]:
        _ = document
        if not violations:
            return []

        return [
            FixOperation(
                action="SET_PAGE_NUMBERING",
                target_element_id=None,
                value=None,
                meta={"number_from_second_page": True, "alignment": "CENTER"},
            )
        ]

