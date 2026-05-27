from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocClassDef:
    class_id: str
    title_ru: str
    recommended_mode: str
    positive_triggers: tuple[str, ...]
    negative_markers: tuple[str, ...] = ()
    disabled_checks: tuple[str, ...] = ()
    forced_mode: str | None = None
    warning: str | None = None


DOC_CLASS_ORDER: tuple[DocClassDef, ...] = (
    DocClassDef(
        class_id="REVIEW",
        title_ru="Отзыв / рецензия",
        recommended_mode="LIGHT",
        positive_triggers=(
            "РЕЦЕНЗИЯ НА ВЫПУСКНУЮ КВАЛИФИКАЦИОННУЮ РАБОТУ",
            "ОТЗЫВ РУКОВОДИТЕЛЯ НА ВЫПУСКНУЮ КВАЛИФИКАЦИОННУЮ РАБОТУ",
            "ОТЗЫВ РУКОВОДИТЕЛЯ НА ДИПЛОМНЫЙ ПРОЕКТ",
            "ОТЗЫВ РУКОВОДИТЕЛЯ",
        ),
        forced_mode="LIGHT",
        disabled_checks=("structural_elements",),
        warning="Это сопроводительный документ. Проверяется только форматирование текста.",
    ),
    DocClassDef(
        class_id="DOCTORAL",
        title_ru="Диплом доктора наук",
        recommended_mode="HARD",
        positive_triggers=(
            "ДИПЛОМ ДОКТОРА НАУК",
            "ДИССЕРТАЦИЯ НА СОИСКАНИЕ УЧЁНОЙ СТЕПЕНИ ДОКТОРА",
            "ДИССЕРТАЦИЯ НА СОИСКАНИЕ УЧЁНОЙ СТЕПЕНИ ДОКТОРА НАУК",
        ),
    ),
    DocClassDef(
        class_id="POSTGRADUATE",
        title_ru="Диплом кандидата наук / аспирантура",
        recommended_mode="HARD",
        positive_triggers=(
            "ДИПЛОМ КАНДИДАТА НАУК",
            "ДИПЛОМ ОБ ОКОНЧАНИИ АСПИРАНТУРЫ",
            "ДИССЕРТАЦИЯ НА СОИСКАНИЕ УЧЁНОЙ СТЕПЕНИ КАНДИДАТА",
            "ДИССЕРТАЦИЯ НА СОИСКАНИЕ УЧЁНОЙ СТЕПЕНИ КАНДИДАТА НАУК",
        ),
    ),
    DocClassDef(
        class_id="THESIS_MASTER",
        title_ru="Магистерская диссертация",
        recommended_mode="HARD",
        positive_triggers=("МАГИСТЕРСКАЯ ДИССЕРТАЦИЯ",),
        negative_markers=(
            "БАКАЛАВРСКАЯ РАБОТА",
            "ДИПЛОМНЫЙ ПРОЕКТ",
            "ДИПЛОМНАЯ РАБОТА",
            "ПО СПЕЦИАЛЬНОСТИ",
        ),
    ),
    DocClassDef(
        class_id="THESIS_BACHELOR",
        title_ru="Бакалаврская работа",
        recommended_mode="HARD",
        positive_triggers=("БАКАЛАВРСКАЯ РАБОТА",),
        negative_markers=(
            "МАГИСТЕРСКАЯ ДИССЕРТАЦИЯ",
            "ДИПЛОМНЫЙ ПРОЕКТ",
            "ДИПЛОМНАЯ РАБОТА",
            "ПО СПЕЦИАЛЬНОСТИ",
        ),
    ),
    DocClassDef(
        class_id="DIPLOMA_SPECIALIST",
        title_ru="Дипломный проект / дипломная работа",
        recommended_mode="HARD",
        positive_triggers=(
            "ДИПЛОМНЫЙ ПРОЕКТ (ДИПЛОМНАЯ РАБОТА)",
            "ДИПЛОМНЫЙ ПРОЕКТ",
            "ДИПЛОМНАЯ РАБОТА",
        ),
        negative_markers=(
            "БАКАЛАВРСКАЯ РАБОТА",
            "МАГИСТЕРСКАЯ ДИССЕРТАЦИЯ",
            "ПО НАПРАВЛЕНИЮ ПОДГОТОВКИ",
        ),
    ),
    DocClassDef(
        class_id="COURSEWORK",
        title_ru="Курсовая работа",
        recommended_mode="MEDIUM",
        positive_triggers=(
            "ПОЯСНИТЕЛЬНАЯ ЗАПИСКА К КУРСОВОЙ РАБОТЕ",
            "ПОЯСНИТЕЛЬНАЯ ЗАПИСКА К КУРСОВОМУ ПРОЕКТУ",
            "ПОЯСНИТЕЛЬНАЯ ЗАПИСКА К КУРСОВОЙ РАБОТЕ (ПРОЕКТУ)",
            "КУРСОВАЯ РАБОТА (ПРОЕКТ)",
            "КУРСОВАЯ РАБОТА",
            "КУРСОВОЙ ПРОЕКТ",
        ),
        negative_markers=(
            "ДОПУСТИТЬ К ЗАЩИТЕ",
            "БАКАЛАВРСКАЯ РАБОТА",
            "МАГИСТЕРСКАЯ ДИССЕРТАЦИЯ",
            "ДИПЛОМНЫЙ ПРОЕКТ",
        ),
    ),
    DocClassDef(
        class_id="LAB_WORK",
        title_ru="Лабораторная работа",
        recommended_mode="LIGHT",
        positive_triggers=(
            "ОТЧЕТ О ЛАБОРАТОРНОЙ РАБОТЕ",
            "ОТЧЕТ О ЛАБОРАТОРНОЙ РАБОТЕ №",
            "ОТЧЁТ О ЛАБОРАТОРНОЙ РАБОТЕ",
            "ЛАБОРАТОРНАЯ РАБОТА",
            "ЛАБОРАТОРНАЯ РАБОТА №",
        ),
        negative_markers=(
            "ДОПУСТИТЬ К ЗАЩИТЕ",
            "ПОЯСНИТЕЛЬНАЯ ЗАПИСКА",
            "БАКАЛАВРСКАЯ РАБОТА",
            "МАГИСТЕРСКАЯ ДИССЕРТАЦИЯ",
            "ДИПЛОМНЫЙ ПРОЕКТ",
            "ДИПЛОМНАЯ РАБОТА",
        ),
        disabled_checks=("structural_elements",),
    ),
    DocClassDef(
        class_id="PRACTICE_WORK",
        title_ru="Контрольная / практическая работа",
        recommended_mode="LIGHT",
        positive_triggers=(
            "КОНТРОЛЬНАЯ РАБОТА",
            "ПРАКТИЧЕСКАЯ РАБОТА",
            "ПРАКТИЧЕСКОЕ ЗАДАНИЕ",
            "ПРАКТИЧЕСКОЕ ЗАНЯТИЕ №",
        ),
        negative_markers=(
            "ДОПУСТИТЬ К ЗАЩИТЕ",
            "ПОЯСНИТЕЛЬНАЯ ЗАПИСКА",
            "ЛАБОРАТОРНОЙ РАБОТЕ",
        ),
        disabled_checks=("structural_elements",),
    ),
    DocClassDef(
        class_id="ESSAY",
        title_ru="Реферат / эссе",
        recommended_mode="LIGHT",
        positive_triggers=(
            "ОЦЕНКА РЕФЕРАТА",
            "РЕФЕРАТ ВЫПОЛНИЛ",
            "РЕФЕРАТ ПО ДИСЦИПЛИНЕ",
            "РЕФЕРАТ НА ТЕМУ",
            "ЭССЕ",
            "МОТИВАЦИОННОЕ ПИСЬМО",
        ),
        negative_markers=(
            "ДОПУСТИТЬ К ЗАЩИТЕ",
            "ПОЯСНИТЕЛЬНАЯ ЗАПИСКА",
            "ЛАБОРАТОРНОЙ РАБОТЕ",
            "КОНТРОЛЬНАЯ РАБОТА",
            "БАКАЛАВРСКАЯ РАБОТА",
        ),
        disabled_checks=("structural_elements",),
    ),
)


DOC_CLASS_BY_ID: dict[str, DocClassDef] = {x.class_id: x for x in DOC_CLASS_ORDER}


ALL_DOC_CLASS_CHOICES: tuple[tuple[str, str], ...] = tuple((x.class_id, x.title_ru) for x in DOC_CLASS_ORDER)

