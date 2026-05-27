from __future__ import annotations


def twips_to_mm(twips: int | float) -> float:
    # 1 twip = 1/1440 inch; 1 inch = 25.4 mm
    return round(float(twips) * 25.4 / 1440.0, 2)

def mm_to_twips(mm: int | float) -> int:
    # 1 twip = 1/1440 inch; 1 inch = 25.4 mm
    return int(round(float(mm) * 1440.0 / 25.4))


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split()).strip()


def normalize_bullets(text: str) -> str:
    """
    Убирает/нормализует маркеры типа “” (как в текущих правках) в типовой вид.
    """
    # В document_corrector.py используется символ "" (часто приходит из Word как “длинное тире”/маркер).
    # Здесь делаем безопасную нормализацию на дефис.
    return text.replace("", "-").replace("−", "-")


def is_blank_paragraph(text: str) -> bool:
    return not normalize_whitespace(text)

