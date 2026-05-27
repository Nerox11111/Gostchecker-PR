from __future__ import annotations

from dataclasses import dataclass, field
from dataclasses import asdict, is_dataclass
from typing import Any

from engine.models.paragraph_model import ParagraphModel
from engine.models.section_model import SectionModel
from engine.models.table_model import TableModel
from engine.models.figure_model import FigureModel
from engine.models.formula_model import FormulaModel
from engine.models.listing_model import ListingModel
from engine.models.violation_model import Violation
from engine.models.zone_model import Zone


@dataclass
class DocumentModel:
    """
    Внутренняя модель документа (единый контейнер данных для парсера/детекторов/чекеров).
    """

    # Элементы документа в порядке следования (упрощённо).
    paragraphs: list[ParagraphModel] = field(default_factory=list)
    tables: list[TableModel] = field(default_factory=list)
    figures: list[FigureModel] = field(default_factory=list)
    formulas: list[FormulaModel] = field(default_factory=list)
    listings: list[ListingModel] = field(default_factory=list)
    sections: list[SectionModel] = field(default_factory=list)

    # Разметка зон (выставляется zone_detector).
    zones: list[Zone] = field(default_factory=list)

    # Стили/настройки/служебные данные, извлечённые парсером.
    styles: dict[str, Any] = field(default_factory=dict)
    page_settings: dict[str, Any] = field(default_factory=dict)
    numbering: dict[str, Any] = field(default_factory=dict)

    # Метаданные для отчётов/отладки.
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_docx_bytes(cls, docx_bytes: bytes) -> "DocumentModel":
        """
        Заглушка. Полный парсер будет реализован на следующем todo.
        """
        from engine.analyzers.document_parser import DocumentParser

        return DocumentParser().parse_docx_bytes(docx_bytes)

    def find_paragraph(self, element_id: str) -> ParagraphModel | None:
        for p in self.paragraphs:
            if p.id == element_id:
                return p
        return None

    def to_dict_summary(self) -> dict[str, Any]:
        metadata = dict(self.metadata)
        # structure_tree содержит SectionNode, поэтому приводим к json-safe форме.
        if "structure_tree" in metadata and metadata["structure_tree"] is not None:
            tree = metadata["structure_tree"]
            if isinstance(tree, list):
                metadata["structure_tree"] = [asdict(x) if is_dataclass(x) else str(x) for x in tree]
            elif is_dataclass(tree):
                metadata["structure_tree"] = asdict(tree)

        return {
            "paragraphs": len(self.paragraphs),
            "tables": len(self.tables),
            "figures": len(self.figures),
            "formulas": len(self.formulas),
            "listings": len(self.listings),
            "sections": len(self.sections),
            "zones": [z.zone_type.value for z in self.zones] if self.zones else [],
            "metadata": metadata,
        }

