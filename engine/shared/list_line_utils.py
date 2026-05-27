from __future__ import annotations

import re

BULLET_PREFIX_RE = re.compile(r"^\s*(?:—|–|-|\*|•|·|▪|◦|→)\s+")
NUMBERED_PREFIX_RE = re.compile(r"^\s*\d+[\.\)]\s+")


def is_bullet_list_line(text: str) -> bool:
    return bool(BULLET_PREFIX_RE.match((text or "").strip()))


def is_numbered_list_line(text: str) -> bool:
    return bool(NUMBERED_PREFIX_RE.match((text or "").strip()))


def is_any_list_line(text: str) -> bool:
    return is_bullet_list_line(text) or is_numbered_list_line(text)
