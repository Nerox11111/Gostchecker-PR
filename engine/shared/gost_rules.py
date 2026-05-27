"""
Структурированное описание правил ГОСТа.

На ранней стадии используем только “точечные” словари, чтобы чекеры могли
иметь единый источник целевых значений.
"""

RULES = {
    "font": {
        "main_family": "Times New Roman",
        "main_size_pt": 14,
        "min_size_pt": 12,
        "mono_family": "Courier New",
        "listing_size_range_pt": (10, 12),
        "line_spacing_main": 1.5,
        "first_line_indent_cm": 1.25,
        "alignment_main": "justify",
    },
    "page": {
        "portrait_margins_mm": {"left": 30, "right": 15, "top": 20, "bottom": 20},
    },
}

