import re


FIGURE_CAPTION_RE = re.compile(r"^Рисунок\s+\d+\s+[—–-]\s+.+[^.]$", re.IGNORECASE)
LISTING_CAPTION_RE = re.compile(r"^Листинг\s+\d+\s+[—–-]\s+.+[^.]$", re.IGNORECASE)

SECTION_TITLE_RE = re.compile(r"^[А-ЯЁ][А-ЯЁA-Z0-9\s\-]+$", re.IGNORECASE)

FORMULA_NUMBER_RE = re.compile(r"\(\s*\d+\s*\)")

# Фразы для заголовка содержания/разделов
TOC_TITLE_RE = re.compile(r"^\s*СОДЕРЖАНИЕ\s*$", re.IGNORECASE)

# TOC: отточия в строке
TOC_DOTS_RE = re.compile(r"\.{3,}")

# Разделы/подразделы: "1", "1.1", "2.3.4" (упрощённо)
SECTION_NUMBER_RE = re.compile(r"^\s*\d+(\.\d+)*\s*$")

# Аббревиатуры в списке: "СОКРАЩЕНИЕ — расшифровка"
ABBREV_LIST_LINE_RE = re.compile(r"^[A-ZА-ЯЁ0-9]{2,}\s*—\s*.+$")

