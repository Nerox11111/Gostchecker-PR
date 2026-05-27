from __future__ import annotations

from dataclasses import dataclass

from engine.models.document_model import DocumentModel


@dataclass
class TocDetector:
    """Эвристики детекции содержания/TOC."""

    def detect(self, document: DocumentModel) -> None:
        # TODO: реализовать.
        return

