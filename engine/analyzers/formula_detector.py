from __future__ import annotations

from dataclasses import dataclass

from engine.models.document_model import DocumentModel
from engine.models.formula_model import FormulaModel
from engine.models.zone_model import ZoneType

import re


@dataclass
class FormulaDetector:
    """Определяет зоны/элементы формул."""

    def detect(self, document: DocumentModel) -> None:
        if not document.paragraphs:
            return

        def contains_omml_xml(p) -> bool:
            if p.xml_element is None:
                return "m:oMath" in (p.xml_ref or "")
            try:
                xml = p.xml_element.xml
            except Exception:
                xml = ""
            return "m:oMath" in xml or "w:instrText" in xml or "OMML" in xml

        formula_re = re.compile(r"формула\s*\(?\s*\d+\s*\)?", re.IGNORECASE)

        formula_idx = 0
        for p in document.paragraphs:
            if p.zone_type == ZoneType.LISTING:
                continue

            if not p.text.strip():
                continue

            if contains_omml_xml(p) or "m:oMath" in (p.xml_ref or ""):
                formula_idx += 1
                p.zone_type = ZoneType.FORMULA
                document.formulas.append(
                    FormulaModel(
                        id=f"formula_{formula_idx}",
                        zone_type=ZoneType.FORMULA,
                        paragraph_id=p.id,
                        page_number=p.page_number,
                        xml_ref=p.xml_ref,
                        numbering_value=None,
                        has_where_block=None,
                    )
                )
                continue

            # Эвристика на “где” блок (отдельный чекер позже).
            if "ГДЕ" in p.text.strip().upper() and formula_re.search(p.text) is None:
                # Не делаем смену зоны здесь, чтобы не ломать разметку;
                # has_where_block будет определяться позже по соседним формулами.
                continue

