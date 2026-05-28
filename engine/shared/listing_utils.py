from __future__ import annotations

import re

from engine.shared.regex_patterns import LISTING_CAPTION_RE

# Однострочные SQL/код маркеры.
SQL_STATEMENT_START_RE = re.compile(
    r"^\s*(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM|CREATE\s+(TABLE|DATABASE|INDEX|VIEW)|"
    r"ALTER\s+TABLE|DROP\s+(TABLE|DATABASE|INDEX|VIEW)|USE|TRUNCATE\s+TABLE|"
    r"ADD\s+CONSTRAINT|CONSTRAINT)\b",
    re.IGNORECASE,
)

SQL_CLAUSE_START_RE = re.compile(
    r"^\s*(FROM|WHERE|JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|INNER\s+JOIN|OUTER\s+JOIN|"
    r"GROUP\s+BY|ORDER\s+BY|HAVING|UNION|VALUES|ON|LIMIT|OFFSET)\b",
    re.IGNORECASE,
)

SQL_KEYWORD_RE = re.compile(
    r"\b(SELECT|FROM|WHERE|JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|INNER\s+JOIN|"
    r"INSERT|UPDATE|DELETE|USE|CREATE|ALTER|DROP|GROUP\s+BY|ORDER\s+BY|"
    r"HAVING|UNION|DISTINCT|INTO|VALUES|TABLE|ON|AS|LIMIT|OFFSET|"
    r"ADD\s+CONSTRAINT|CONSTRAINT)\b",
    re.IGNORECASE,
)

CODE_SYNTAX_RE = re.compile(
    r"^\s*(def|class|if|elif|else|for|while|try|except|finally|with|import|from|"
    r"return|function|const|let|var|public|private|protected|static|void|int|"
    r"string|bool|boolean|float|double|using|namespace|package)\b|"
    r"[{}]|==|!=|<=|>=|&&|\|\||:=|=>|->|^\s*//|/\*|\*/",
    re.IGNORECASE,
)

ASSIGNMENT_RE = re.compile(r"^\s*[A-Za-z_][\w.,\s\[\]]*\s*=\s*[^=]")
URL_RE = re.compile(r"\b(?:https?://|www\.)\S+", re.IGNORECASE)
REFERENCE_MARKER_RE = re.compile(r"(//\s*URL:|URL:|https?://)", re.IGNORECASE)
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")


def is_listing_caption_text(text: str) -> bool:
    return bool(LISTING_CAPTION_RE.match((text or "").strip()))


def _has_cyrillic(text: str) -> bool:
    return bool(CYRILLIC_RE.search(text))


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def looks_like_prose_line(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    if not _has_cyrillic(t):
        return False
    if SQL_STATEMENT_START_RE.match(t) or SQL_CLAUSE_START_RE.match(t):
        return False
    if REFERENCE_MARKER_RE.search(t):
        return True
    return _word_count(t) >= 8 or bool(re.search(r"[.!?]\s*$", t))


def looks_like_listing_continuation(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    if looks_like_code_line(t):
        return True
    if looks_like_prose_line(t):
        return False
    if CODE_SYNTAX_RE.search(t):
        return True
    if re.search(r"[,;({}\[\])]\s*$", t):
        return True
    if re.match(r"^\s*[-+*/%#]", t):
        return True
    return not _has_cyrillic(t) and _word_count(t) <= 10


def looks_like_code_line(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    if is_listing_caption_text(t):
        return False
    if looks_like_prose_line(t):
        return False
    if REFERENCE_MARKER_RE.search(t) and _has_cyrillic(t):
        return False
    if _has_cyrillic(t) and _word_count(t) >= 6:
        return False
    if SQL_STATEMENT_START_RE.match(t):
        return True
    if SQL_CLAUSE_START_RE.match(t) and (not _has_cyrillic(t) or _word_count(t) <= 12):
        return True
    # Короткие команды вроде "use store;"
    if CODE_SYNTAX_RE.search(t):
        return True
    if ASSIGNMENT_RE.search(t) and not URL_RE.search(t):
        return True
    sql_hits = SQL_KEYWORD_RE.findall(t)
    if len(sql_hits) >= 2 and not _has_cyrillic(t):
        return True
    if t.endswith(";") and not _has_cyrillic(t) and (
        bool(SQL_KEYWORD_RE.search(t)) or _word_count(t) <= 12
    ):
        return True
    return False


def is_listing_block_boundary(text: str) -> bool:
    upper = (text or "").strip().upper()
    if not upper:
        return False
    if upper in {
        "СОДЕРЖАНИЕ",
        "ВВЕДЕНИЕ",
        "ЗАКЛЮЧЕНИЕ",
        "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ",
        "ПРИЛОЖЕНИЯ",
        "ПРИЛОЖЕНИЕ",
    }:
        return True
    if upper.startswith("РИСУНОК ") or upper.startswith("РИС. "):
        return True
    if upper.startswith("ТАБЛИЦА "):
        return True
    if is_listing_caption_text(text):
        return True
    return False
