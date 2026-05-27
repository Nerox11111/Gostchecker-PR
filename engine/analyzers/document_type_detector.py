from __future__ import annotations

from dataclasses import dataclass

from engine.analyzers.title_page_detector import TitlePageDetector
from engine.models.document_model import DocumentModel
from engine.shared.doc_classification import ALL_DOC_CLASS_CHOICES, DOC_CLASS_ORDER


@dataclass
class DocumentTypeDetector:
    scan_first_paragraphs: int = 40

    def detect(self, document: DocumentModel) -> dict[str, object]:
        title = TitlePageDetector().detect(document)
        paragraphs = [p.text.strip().upper() for p in document.paragraphs[: self.scan_first_paragraphs] if p.text.strip()]
        joined = "\n".join(paragraphs)

        matched_class = None
        matched_trigger = None

        for cls in DOC_CLASS_ORDER:
            has_negative = any(neg in joined for neg in cls.negative_markers)
            if has_negative:
                continue
            trigger = next((t for t in cls.positive_triggers if t in joined), None)
            if trigger:
                matched_class = cls
                matched_trigger = trigger
                break

        if matched_class is None:
            return {
                "detected": False,
                "class_id": None,
                "title_ru": None,
                "recommended_mode": None,
                "forced_mode": None,
                "warning": None,
                "matched_trigger": None,
                "disabled_checks": [],
                "choices": [{"class_id": cid, "title_ru": name} for cid, name in ALL_DOC_CLASS_CHOICES],
                "title_page": title,
            }

        return {
            "detected": True,
            "class_id": matched_class.class_id,
            "title_ru": matched_class.title_ru,
            "recommended_mode": matched_class.recommended_mode,
            "forced_mode": matched_class.forced_mode,
            "warning": matched_class.warning,
            "matched_trigger": matched_trigger,
            "disabled_checks": list(matched_class.disabled_checks),
            "choices": [{"class_id": cid, "title_ru": name} for cid, name in ALL_DOC_CLASS_CHOICES],
            "title_page": title,
        }

