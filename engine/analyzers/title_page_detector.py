from __future__ import annotations

import re
from dataclasses import dataclass

from engine.models.document_model import DocumentModel
from engine.models.paragraph_model import ParagraphModel
from engine.shared.figure_caption_utils import assign_paragraph_page_numbers
from engine.shared.title_page_keywords import (
    TITLE_PAGE_AUTHOR_MARKERS,
    TITLE_PAGE_CITY_YEAR_PATTERNS,
    TITLE_PAGE_DEPARTMENT_VARIANTS,
    TITLE_PAGE_PERSON_NAME_RE,
    TITLE_PAGE_REPORT_MARKERS,
    TITLE_PAGE_UNIVERSITY_VARIANTS,
    TITLE_PAGE_WORK_TYPE_VARIANTS,
)


@dataclass
class TitlePageDetector:
    """Эвристики детекции титульного листа (первые 1–2 страницы)."""

    title_page_confidence_threshold: float = 0.35
    max_pages_to_scan: int = 2

    def detect(self, document: DocumentModel) -> dict[str, object]:
        paragraphs = self._paragraphs_on_first_pages(document.paragraphs)
        matched = self._match_keywords(paragraphs)
        score = self._score(matched, paragraphs)
        confidence = max(0.0, min(1.0, score))
        is_title_page = confidence >= 0.6

        texts = [p.text for p in paragraphs if p.text]
        return {
            "is_title_page": is_title_page,
            "confidence": confidence,
            "matched_keywords": matched,
            "pages_scanned": self.max_pages_to_scan,
            "paragraphs_scanned": len(paragraphs),
            "title_page_paragraph_ids": [p.id for p in paragraphs] if confidence >= self.title_page_confidence_threshold else [],
            "joined_preview": "\n".join(texts)[:600],
        }

    def detect_title_page_paragraph_ids(self, document: DocumentModel) -> set[str]:
        """ID параграфов на 1–2 страницах, если найдено достаточно ключевых слов."""
        paragraphs = self._paragraphs_on_first_pages(document.paragraphs)
        if not paragraphs:
            return set()

        matched = self._match_keywords(paragraphs)
        score = self._score(matched, paragraphs)
        if score < self.title_page_confidence_threshold:
            return set()
        return {p.id for p in paragraphs}

    def _paragraphs_on_first_pages(self, paragraphs: list[ParagraphModel]) -> list[ParagraphModel]:
        if not paragraphs:
            return []
        page_by_id = assign_paragraph_page_numbers(paragraphs)
        return [p for p in paragraphs if page_by_id.get(p.id, 1) <= self.max_pages_to_scan]

    def _match_keywords(self, paragraphs: list[ParagraphModel]) -> dict[str, list[str]]:
        texts = [p.text for p in paragraphs if p.text]
        joined = "\n".join(texts).upper()

        matched: dict[str, list[str]] = {
            "work_type": [],
            "university": [],
            "department": [],
            "author_markers": [],
            "city_year": [],
            "report_markers": [],
            "person_name": [],
        }

        for kw in TITLE_PAGE_WORK_TYPE_VARIANTS:
            if kw in joined:
                matched["work_type"].append(kw)

        for kw in TITLE_PAGE_UNIVERSITY_VARIANTS:
            if kw in joined:
                matched["university"].append(kw)

        for kw in TITLE_PAGE_DEPARTMENT_VARIANTS:
            if kw in joined:
                matched["department"].append(kw)

        for kw in TITLE_PAGE_AUTHOR_MARKERS:
            if kw in joined:
                matched["author_markers"].append(kw)

        for kw in TITLE_PAGE_REPORT_MARKERS:
            if kw in joined:
                matched["report_markers"].append(kw)

        for pat in TITLE_PAGE_CITY_YEAR_PATTERNS:
            if re.search(pat, joined):
                matched["city_year"].append(pat)

        full_text = "\n".join(texts)
        if re.search(TITLE_PAGE_PERSON_NAME_RE, full_text):
            matched["person_name"].append("ФИО (И.О.)")

        return matched

    @staticmethod
    def _score(matched: dict[str, list[str]], paragraphs: list[ParagraphModel]) -> float:
        score = 0.0
        if matched["work_type"]:
            score += 0.22
        if matched["university"]:
            score += 0.18
        if matched["department"]:
            score += 0.16
        if matched["city_year"]:
            score += 0.16
        if matched["author_markers"]:
            score += 0.12
        if matched["report_markers"]:
            score += 0.08
        if matched["person_name"]:
            score += 0.08

        center_aligned = sum(
            1
            for p in paragraphs
            if (p.alignment or "").upper() in {"CENTER", "ЦЕНТР", "WD_ALIGN_PARAGRAPH.CENTER (1)"}
            or "(1)" in str(p.alignment or "")
        )
        if center_aligned >= 2:
            score = min(1.0, score + 0.05)

        # Доля непустых категорий ключевых слов.
        categories = [k for k, v in matched.items() if v]
        if len(categories) >= 3:
            score = min(1.0, score + 0.05)

        return score
