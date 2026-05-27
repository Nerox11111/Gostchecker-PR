from __future__ import annotations

import re
from dataclasses import dataclass

from engine.core.fixer import BaseFixer
from engine.models.document_model import DocumentModel
from engine.models.violation_model import FixOperation, Violation
from engine.shared.constants import (
    GOST_FIRST_LINE_INDENT_CM,
    GOST_LINE_SPACING_MAIN,
    GOST_MAIN_FONT_NAME,
    GOST_MAIN_FONT_SIZE_PT,
)
from engine.shared.list_line_utils import BULLET_PREFIX_RE, NUMBERED_PREFIX_RE, is_any_list_line


MAIN_FMT = {
    "alignment": "JUSTIFY",
    "first_line_indent_cm": GOST_FIRST_LINE_INDENT_CM,
    "line_spacing": GOST_LINE_SPACING_MAIN,
    "font_name": GOST_MAIN_FONT_NAME,
    "font_size_pt": GOST_MAIN_FONT_SIZE_PT,
    "bold": False,
    "italic": False,
    "underline": False,
}
LIST_NUMBER_FMT = {
    "font_name": GOST_MAIN_FONT_NAME,
    "font_size_pt": GOST_MAIN_FONT_SIZE_PT,
    "bold": False,
    "italic": False,
    "underline": False,
}


@dataclass
class ListMarkerFixer:
    def supported_violation_codes(self) -> set[str]:
        return {"LIST_MARKER_WRONG", "LIST_NUMBERING_ORDER", "LIST_NUMBER_FORMAT_WRONG"}

    def build_fixes(self, document: DocumentModel, violations: list[Violation]) -> list[FixOperation]:
        ops: list[FixOperation] = []

        wrong_marker_ids = {v.element_id for v in violations if v.code == "LIST_MARKER_WRONG"}
        wrong_number_ids = {v.element_id for v in violations if v.code == "LIST_NUMBERING_ORDER"}
        wrong_number_format_ids = {v.element_id for v in violations if v.code == "LIST_NUMBER_FORMAT_WRONG"}

        formatted_lists: set[str] = set()
        if wrong_number_format_ids:
            ops.append(
                FixOperation(
                    action="SET_LIST_NUMBER_FORMAT",
                    target_element_id=None,
                    meta={
                        **LIST_NUMBER_FMT,
                        "style_names": sorted(
                            {
                                p.style_name
                                for p in document.paragraphs
                                if p.id in wrong_number_format_ids and p.style_name
                            }
                        ),
                    },
                )
            )

        def add_main_format(pid: str) -> None:
            if pid in formatted_lists:
                return
            formatted_lists.add(pid)
            ops.append(
                FixOperation(
                    action="SET_PARAGRAPH_FORMAT",
                    target_element_id=pid,
                    meta=dict(MAIN_FMT),
                )
            )

        for p in document.paragraphs:
            if p.id in wrong_marker_ids:
                text = (p.text or "").strip()
                m = BULLET_PREFIX_RE.match(text)
                if m:
                    rest = text[m.end() :].strip()
                    new_text = f"— {rest}" if rest else "—"
                    ops.append(
                        FixOperation(
                            action="SET_PARAGRAPH_TEXT",
                            target_element_id=p.id,
                            value=new_text,
                            meta={"alignment": "JUSTIFY"},
                        )
                    )
                add_main_format(p.id)

        block: list[str] = []

        def flush_block() -> None:
            nonlocal block
            if len(block) < 2:
                for pid in block:
                    add_main_format(pid)
                block = []
                return
            for idx, element_id in enumerate(block, start=1):
                p = next((x for x in document.paragraphs if x.id == element_id), None)
                if not p:
                    continue
                txt = (p.text or "").strip()
                m = NUMBERED_PREFIX_RE.match(txt)
                if m:
                    tail = txt[m.end() :].strip()
                    new_text = f"{idx}. {tail}" if tail else f"{idx}."
                    ops.append(
                        FixOperation(
                            action="SET_PARAGRAPH_TEXT",
                            target_element_id=element_id,
                            value=new_text,
                            meta={"alignment": "JUSTIFY"},
                        )
                    )
                add_main_format(element_id)
            block = []

        for p in document.paragraphs:
            text = (p.text or "").strip()
            if not text:
                flush_block()
                continue
            if NUMBERED_PREFIX_RE.match(text):
                if p.id in wrong_number_ids or p.id in wrong_number_format_ids or block:
                    block.append(p.id)
                elif is_any_list_line(text):
                    add_main_format(p.id)
                continue
            flush_block()
            if p.id in wrong_number_format_ids or is_any_list_line(text):
                add_main_format(p.id)
        flush_block()

        return ops
