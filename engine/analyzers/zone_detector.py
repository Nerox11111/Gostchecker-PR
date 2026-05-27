from __future__ import annotations

from dataclasses import dataclass

from engine.analyzers.figure_detector import FigureDetector
from engine.analyzers.title_page_detector import TitlePageDetector
from engine.models.document_model import DocumentModel
from engine.models.zone_model import Zone, ZoneType
from engine.shared.regex_patterns import TOC_DOTS_RE, TOC_TITLE_RE


@dataclass
class ZoneDetector:
    """Определяет зоны документа (TITLE_PAGE/TOC/MAIN_CONTENT/...)."""

    def detect_zones(self, document: DocumentModel) -> list[object]:
        paragraphs = document.paragraphs
        if not paragraphs:
            document.zones = []
            return []

        def _find_first_index(pred) -> int | None:
            for i, p in enumerate(paragraphs):
                if pred(p):
                    return i
            return None

        toc_idx = _find_first_index(lambda p: bool(TOC_TITLE_RE.match(p.text)))
        intro_idx = _find_first_index(lambda p: p.text.strip().upper().startswith("ВВЕДЕНИЕ"))
        bibliography_idx = _find_first_index(
            lambda p: "СПИСОК" in p.text.upper() and "ИСТОЧНИК" in p.text.upper()
        )
        appendix_idx = _find_first_index(
            lambda p: p.text.strip().upper().startswith("ПРИЛОЖЕНИЕ")
            or p.text.strip().upper().startswith("ПРИЛОЖЕНИЯ")
        )

        toc_idx = toc_idx if toc_idx is not None else 0
        intro_idx = intro_idx if intro_idx is not None else (toc_idx + 1 if toc_idx > 0 else 1)
        bibliography_idx = bibliography_idx if bibliography_idx is not None else len(paragraphs)
        appendix_idx = appendix_idx if appendix_idx is not None else len(paragraphs)

        for p in paragraphs:
            p.zone_type = None

        # Титульные листы: эвристика по ключевым словам на первых 2 страницах.
        title_page_ids = TitlePageDetector().detect_title_page_paragraph_ids(document)
        if title_page_ids:
            for p in paragraphs:
                if p.id in title_page_ids:
                    p.zone_type = ZoneType.TITLE_PAGE
        elif toc_idx > 0:
            for p in paragraphs[:toc_idx]:
                p.zone_type = ZoneType.TITLE_PAGE

        # TOC.
        for p in paragraphs[toc_idx:intro_idx]:
            if p.zone_type is None:
                p.zone_type = ZoneType.TOC

        # MAIN_CONTENT.
        main_end = min(bibliography_idx, appendix_idx)
        for p in paragraphs[intro_idx:main_end]:
            if p.zone_type is None:
                p.zone_type = ZoneType.MAIN_CONTENT

        for p in paragraphs[main_end:bibliography_idx]:
            if p.zone_type is None:
                p.zone_type = ZoneType.BIBLIOGRAPHY

        for p in paragraphs[bibliography_idx:appendix_idx]:
            if p.zone_type is None:
                p.zone_type = ZoneType.APPENDIX

        for t in document.tables:
            t.zone_type = ZoneType.TABLE

        from engine.analyzers.listing_detector import ListingDetector
        from engine.analyzers.formula_detector import FormulaDetector

        ListingDetector().detect(document)
        FormulaDetector().detect(document)
        FigureDetector().detect(document)

        zones: list[Zone] = []
        zone_types: list[ZoneType] = [
            ZoneType.TITLE_PAGE,
            ZoneType.TOC,
            ZoneType.MAIN_CONTENT,
            ZoneType.TABLE,
            ZoneType.FIGURE,
            ZoneType.FORMULA,
            ZoneType.LISTING,
            ZoneType.BIBLIOGRAPHY,
            ZoneType.APPENDIX,
        ]

        for zt in zone_types:
            ids: list[str] = []
            if zt == ZoneType.TABLE:
                ids = [t.id for t in document.tables]
            else:
                ids = [p.id for p in paragraphs if p.zone_type == zt]

            if not ids:
                continue
            zones.append(Zone(id=f"zone_{zt.value}", zone_type=zt, element_ids=ids))

        document.zones = zones
        return zones
