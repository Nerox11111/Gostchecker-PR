"""
Константы ГОСТ-ограничений и “целевых” значений форматирования.

На этапе MVP это будут базовые значения; далее уточним под требования документа.
"""

GOST_MAIN_FONT_NAME = "Times New Roman"
GOST_MONO_FONT_NAME = "Courier New"

GOST_MAIN_FONT_SIZE_PT = 14
GOST_MIN_FONT_SIZE_PT = 12

GOST_LISTING_FONT_SIZE_PT_MIN = 10
GOST_LISTING_FONT_SIZE_PT_MAX = 12

GOST_LINE_SPACING_MAIN = 1.5
GOST_FIRST_LINE_INDENT_CM = 1.25
GOST_LEFT_INDENT_CM = 0.0
GOST_RIGHT_INDENT_CM = 0.0
GOST_SPACE_BEFORE_PT = 0.0
GOST_SPACE_AFTER_PT = 0.0

GOST_LISTING_LINE_SPACING = 1.15
GOST_LISTING_INDENT_CM = 2.0

GOST_PAGE_MARGINS_PORTRAIT_MM = {"left": 30, "right": 15, "top": 20, "bottom": 20}
GOST_PAGE_MARGINS_LANDSCAPE_MM = {"left": 20, "right": 20, "top": 15, "bottom": 30}

# Секции/зоны
GOST_REQUIRED_SECTIONS = [
    "СОДЕРЖАНИЕ",
    "ВВЕДЕНИЕ",
    "ЗАКЛЮЧЕНИЕ",
    "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ",
    "ПРИЛОЖЕНИЯ",
]

