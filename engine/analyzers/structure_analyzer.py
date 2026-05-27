from __future__ import annotations

from dataclasses import dataclass

from engine.models.document_model import DocumentModel
from engine.models.structure_node_model import SectionNode
from engine.shared.constants import GOST_REQUIRED_SECTIONS
from engine.shared.regex_patterns import SECTION_NUMBER_RE


@dataclass
class StructureAnalyzer:
    """Строит дерево структуры разделов и отмечает обязательные блоки."""

    def analyze(self, document: DocumentModel) -> None:
        headings: list[dict] = []

        def detect_level(text: str) -> tuple[int, str | None]:
            t = text.strip()
            if not t:
                return 0, None
            upper = t.upper()
            if upper in (s.upper() for s in GOST_REQUIRED_SECTIONS):
                return 1, None
            if SECTION_NUMBER_RE.match(t):
                # "1" -> 1, "1.1" -> 2 ...
                num_parts = [x for x in t.strip().split(".") if x]
                return max(1, len(num_parts)), t.strip()
            return 0, None

        for p in document.paragraphs:
            if not p.text.strip():
                continue

            level, number_str = detect_level(p.text)
            if level <= 0:
                continue

            headings.append(
                {
                    "element_id": p.id,
                    "title": p.text.strip(),
                    "level": level,
                    "number_str": number_str,
                    "starts_with_page_break": p.starts_with_page_break,
                    "zone_type": p.zone_type,
                }
            )

        # Построение дерева.
        roots: list[SectionNode] = []
        stack: list[SectionNode] = []

        for h in headings:
            level = h["level"]
            node = SectionNode(
                element_id=h["element_id"],
                title=h["title"],
                level=level,
                number_str=h["number_str"],
            )

            if level <= 1 or not stack:
                roots.append(node)
                stack = [node]
                continue

            parent_level = level - 1
            parent = stack[parent_level - 1] if parent_level - 1 < len(stack) else None
            if parent is not None:
                parent.children.append(node)

            # Обновляем стек до текущего уровня.
            stack = stack[: level - 1]
            stack.append(node)

        found_required = {h["title"].upper() for h in headings if h["number_str"] is None}
        missing_required = [s for s in GOST_REQUIRED_SECTIONS if s.upper() not in found_required]

        document.metadata["structure_headings"] = headings
        document.metadata["structure_tree"] = roots
        document.metadata["missing_required_sections"] = missing_required

