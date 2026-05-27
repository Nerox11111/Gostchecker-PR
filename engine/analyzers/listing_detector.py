from __future__ import annotations

from dataclasses import dataclass

from engine.models.document_model import DocumentModel
from engine.models.listing_model import ListingModel
from engine.models.zone_model import ZoneType
from engine.shared.listing_utils import (
    is_listing_block_boundary,
    is_listing_caption_text,
    looks_like_code_line,
    looks_like_listing_continuation,
)


@dataclass
class ListingDetector:
    """Определяет зоны листингов: подпись — обычный текст, код — LISTING."""

    def detect(self, document: DocumentModel) -> None:
        if not document.paragraphs:
            return

        marked: set[str] = set()
        listing_idx = 0

        for i, p in enumerate(document.paragraphs):
            if p.id in marked:
                continue
            if not (p.text or "").strip():
                continue

            if not is_listing_caption_text(p.text):
                continue

            listing_idx += 1
            # Подпись листинга НЕ помечаем как LISTING (остаётся MAIN_CONTENT / текущая зона).
            marked.add(p.id)

            code_ids: list[str] = []
            in_block = False
            empty_streak = 0

            for j in range(i + 1, len(document.paragraphs)):
                pj = document.paragraphs[j]
                text = (pj.text or "").strip()

                if is_listing_block_boundary(text) and j != i:
                    break

                if not text:
                    empty_streak += 1
                    if in_block and empty_streak >= 2:
                        break
                    continue

                empty_streak = 0

                if in_block:
                    if not looks_like_listing_continuation(text):
                        break
                    pj.zone_type = ZoneType.LISTING
                    marked.add(pj.id)
                    code_ids.append(pj.id)
                    continue

                if looks_like_code_line(text):
                    in_block = True
                    pj.zone_type = ZoneType.LISTING
                    marked.add(pj.id)
                    code_ids.append(pj.id)

            document.listings.append(
                ListingModel(
                    id=f"listing_{listing_idx}",
                    zone_type=ZoneType.LISTING,
                    page_number=p.page_number,
                    xml_ref=p.xml_ref,
                    caption_paragraph_id=p.id,
                    code_container_paragraph_id=code_ids[0] if code_ids else None,
                )
            )

        # Fallback: кодовый блок может быть без подписи "Листинг ...".
        for i, p in enumerate(document.paragraphs):
            if p.id in marked:
                continue
            text = (p.text or "").strip()
            if not text:
                continue
            if not looks_like_code_line(text):
                continue
            # Старт блока: текущая строка похожа на код.
            listing_idx += 1
            code_ids: list[str] = []
            for j in range(i, len(document.paragraphs)):
                pj = document.paragraphs[j]
                t = (pj.text or "").strip()
                if not t:
                    if code_ids:
                        # Одна пустая строка допустима внутри блока.
                        continue
                    break
                if is_listing_block_boundary(t) and j != i:
                    break
                if code_ids and not looks_like_listing_continuation(t):
                    break
                pj.zone_type = ZoneType.LISTING
                marked.add(pj.id)
                code_ids.append(pj.id)
                # после старта блока берём все непустые строки до границы
                # чтобы фикс применялся ко всему куску кода.
            if code_ids:
                document.listings.append(
                    ListingModel(
                        id=f"listing_{listing_idx}",
                        zone_type=ZoneType.LISTING,
                        page_number=p.page_number,
                        xml_ref=p.xml_ref,
                        caption_paragraph_id=None,
                        code_container_paragraph_id=code_ids[0],
                    )
                )
