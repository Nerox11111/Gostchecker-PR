from __future__ import annotations

from dataclasses import dataclass

from engine.models.document_model import DocumentModel
from engine.models.zone_model import ZoneType
from engine.shared.figure_caption_utils import is_figure_caption_text


@dataclass
class FigureDetector:
    """Помечает параграфы с подписью рисунка зоной FIGURE."""

    def detect(self, document: DocumentModel) -> None:
        for p in document.paragraphs:
            if getattr(p, "in_table", False):
                continue
            if is_figure_caption_text(p.text or ""):
                p.zone_type = ZoneType.FIGURE
