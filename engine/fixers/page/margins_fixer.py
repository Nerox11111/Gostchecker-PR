from __future__ import annotations

from dataclasses import dataclass

from engine.core.fixer import BaseFixer
from engine.models.document_model import DocumentModel
from engine.models.violation_model import FixOperation, Violation
from engine.shared.constants import GOST_PAGE_MARGINS_LANDSCAPE_MM, GOST_PAGE_MARGINS_PORTRAIT_MM


@dataclass
class MarginsFixer:
    """Исправляет поля страницы."""

    def supported_violation_codes(self) -> set[str]:
        return {"PAGE_MARGINS_INVALID"}

    def build_fixes(self, document: DocumentModel, violations: list[Violation]) -> list[FixOperation]:
        if not violations:
            return []

        if not document.sections:
            # Упадём позже при применении, но так проще сохранить архитектуру.
            margins = GOST_PAGE_MARGINS_PORTRAIT_MM
        else:
            orientation = (document.sections[0].orientation or "").upper()
            margins = GOST_PAGE_MARGINS_LANDSCAPE_MM if "LANDSCAPE" in orientation else GOST_PAGE_MARGINS_PORTRAIT_MM

        return [
            FixOperation(
                action="SET_PAGE_MARGINS",
                target_element_id=None,
                value=None,
                meta={"margins_mm": margins},
            )
        ]

