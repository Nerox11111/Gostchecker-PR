from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from engine.core.document_engine import DocumentEngine, DocumentEngineConfig
from engine.core.fixer import Fixer
from engine.core.report_builder import JsonReportBuilder
from engine.core.validator import Validator
from engine.models.document_model import DocumentModel
from engine.analyzers.document_type_detector import DocumentTypeDetector

from engine.checkers.font.font_family_checker import FontFamilyChecker
from engine.checkers.font.font_size_checker import FontSizeChecker
from engine.checkers.font.font_style_checker import FontStyleChecker
from engine.checkers.font.font_spacing_checker import FontSpacingChecker
from engine.checkers.page.margins_checker import MarginsChecker
from engine.checkers.page.page_numbering_checker import PageNumberingChecker
from engine.checkers.page.title_page_numbering_checker import TitlePageNumberingChecker
from engine.checkers.structure.structural_elements_checker import StructuralElementsChecker
from engine.checkers.tables.table_caption_checker import TableCaptionChecker
from engine.checkers.formulas.formula_format_checker import FormulaFormatChecker
from engine.checkers.listings.listing_format_checker import ListingFormatChecker
from engine.checkers.figures.figure_caption_checker import FigureCaptionChecker
from engine.checkers.figures.figure_layout_checker import FigureLayoutChecker
from engine.checkers.lists.list_marker_checker import ListMarkerChecker

from engine.fixers.font.font_format_fixer import FontFormatFixer
from engine.fixers.page.margins_fixer import MarginsFixer
from engine.fixers.page.page_numbering_fixer import PageNumberingFixer
from engine.fixers.figures.figure_caption_fixer import FigureCaptionFixer
from engine.fixers.figures.figure_layout_fixer import FigureLayoutFixer
from engine.fixers.lists.list_marker_fixer import ListMarkerFixer

from engine.shared.title_page_keywords import (
    TITLE_PAGE_AUTHOR_MARKERS,
    TITLE_PAGE_CITY_YEAR_PATTERNS,
    TITLE_PAGE_DEPARTMENT_VARIANTS,
    TITLE_PAGE_REPORT_MARKERS,
    TITLE_PAGE_UNIVERSITY_VARIANTS,
    TITLE_PAGE_WORK_TYPE_VARIANTS,
)
from engine.shared.doc_classification import ALL_DOC_CLASS_CHOICES, DOC_CLASS_BY_ID


app = FastAPI(title="GostChecker backend (local temp)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@dataclass(frozen=True)
class ScopeDef:
    scope_id: str
    title: str
    checkers: list[str]
    fixers: list[str]
    description: str


CHECKER_MAP: dict[str, Any] = {
    "margins": MarginsChecker(),
    "page_numbering": PageNumberingChecker(),
    "title_page_numbering": TitlePageNumberingChecker(),
    "font_family": FontFamilyChecker(),
    "font_size": FontSizeChecker(),
    "font_style": FontStyleChecker(),
    "font_spacing": FontSpacingChecker(),
    "structural_elements": StructuralElementsChecker(),
    "table_caption": TableCaptionChecker(),
    "formula_format": FormulaFormatChecker(),
    "listing_format": ListingFormatChecker(),
    "figure_caption": FigureCaptionChecker(),
    "figure_layout": FigureLayoutChecker(),
    "list_marker": ListMarkerChecker(),
}

FIXER_MAP: dict[str, Any] = {
    "margins": MarginsFixer(),
    "page_numbering": PageNumberingFixer(),
    "font_format": FontFormatFixer(),
    "figure_caption": FigureCaptionFixer(),
    "figure_layout": FigureLayoutFixer(),
    "list_marker": ListMarkerFixer(),
}

SCOPES: list[ScopeDef] = [
    ScopeDef(
        scope_id="validate_all_key",
        title="Валидация: все ключевые проверки",
        checkers=list(CHECKER_MAP.keys()),
        fixers=[],
        description="Запускает набор реализованных чекеров (шрифты/поля/структура/подписи/формулы/листинги).",
    ),
    ScopeDef(
        scope_id="validate_font",
        title="Валидация: шрифты",
        checkers=["font_family", "font_size", "font_style", "font_spacing"],
        fixers=[],
        description="Проверка соответствия шрифтовым требованиям основного текста.",
    ),
    ScopeDef(
        scope_id="validate_page",
        title="Валидация: поля/нумерация",
        checkers=["margins", "page_numbering", "title_page_numbering"],
        fixers=[],
        description="Поля страницы и нумерация PAGE в нижнем колонтитуле.",
    ),
    ScopeDef(
        scope_id="validate_structure",
        title="Валидация: структура",
        checkers=["structural_elements"],
        fixers=[],
        description="Наличие обязательных структурных элементов.",
    ),
    ScopeDef(
        scope_id="validate_tables",
        title="Валидация: подписи таблиц",
        checkers=["table_caption"],
        fixers=[],
        description="Формат подписи \"Таблица N — Наименование\".",
    ),
    ScopeDef(
        scope_id="validate_formulas",
        title="Валидация: формат формул",
        checkers=["formula_format"],
        fixers=[],
        description="Простейшая проверка выравнивания и номера в скобках.",
    ),
    ScopeDef(
        scope_id="validate_listings",
        title="Валидация: формат листингов",
        checkers=["listing_format"],
        fixers=[],
        description="Шрифт/размер/интервалы/отступы в листингах (эвристика по моноширинному шрифту).",
    ),
    ScopeDef(
        scope_id="validate_lists",
        title="Валидация: списки",
        checkers=["list_marker"],
        fixers=[],
        description="Проверка маркеров и последовательности нумерации списков.",
    ),
    ScopeDef(
        scope_id="validate_figures",
        title="Валидация: подписи рисунков",
        checkers=["figure_caption", "figure_layout"],
        fixers=[],
        description='Формат подписи «Рисунок N — Наименование».',
    ),
    ScopeDef(
        scope_id="correct_all",
        title="Коррекция: все ключевые фиксы",
        checkers=list(CHECKER_MAP.keys()),
        fixers=["margins", "page_numbering", "font_format", "figure_caption", "figure_layout", "list_marker"],
        description="Применяет фиксы к полям/нумерации/шрифтам/подписям рисунков и перепроверяет документ.",
    ),
    ScopeDef(
        scope_id="correct_page",
        title="Коррекция: поля/страницы",
        checkers=["margins", "page_numbering", "title_page_numbering"],
        fixers=["margins", "page_numbering"],
        description="Исправляет поля и добавляет нумерацию PAGE в footer.",
    ),
    ScopeDef(
        scope_id="correct_font",
        title="Коррекция: шрифты",
        checkers=["font_family", "font_size", "font_style", "font_spacing"],
        fixers=["font_format"],
        description="Приводит основной текст и листинги к целевым шрифтовым параметрам.",
    ),
    ScopeDef(
        scope_id="correct_figures",
        title="Коррекция: подписи рисунков",
        checkers=["figure_caption", "figure_layout"],
        fixers=["figure_caption", "figure_layout"],
        description='Исправляет подписи вида «Рис. N. …» на «Рисунок N — …».',
    ),
    ScopeDef(
        scope_id="correct_lists",
        title="Коррекция: списки",
        checkers=["list_marker"],
        fixers=["list_marker"],
        description="Исправляет маркеры ненумерованных списков и нумерацию блоков.",
    ),
]

SCOPE_INDEX = {s.scope_id: s for s in SCOPES}

CHECKER_TITLES_RU: dict[str, str] = {
    "margins": "Поля страницы",
    "page_numbering": "Нумерация страниц",
    "title_page_numbering": "Нумерация титульного листа",
    "font_family": "Шрифт основного текста",
    "font_size": "Размер шрифта",
    "font_style": "Стиль шрифта (подчеркивание и т.п.)",
    "font_spacing": "Интервалы, отступы и выравнивание",
    "structural_elements": "Обязательные структурные разделы",
    "table_caption": "Формат подписей таблиц",
    "formula_format": "Формат формул",
    "listing_format": "Формат листингов кода",
    "figure_caption": "Формат подписей рисунков",
    "figure_layout": "Выравнивание рисунков",
    "list_marker": "Маркеры и нумерация списков",
}

PROFILE_CHECKERS: dict[str, list[str]] = {
    "LIGHT": [
        "margins",
        "font_family",
        "font_size",
        "font_style",
        "font_spacing",
        "table_caption",
        "figure_caption",
        "listing_format",
    ],
    "MEDIUM": [
        "margins",
        "font_family",
        "font_size",
        "font_style",
        "font_spacing",
        "table_caption",
        "figure_caption",
        "listing_format",
        "formula_format",
        "figure_layout",
        "list_marker",
    ],
    "HARD": list(CHECKER_MAP.keys()),
}


@dataclass(frozen=True)
class MethodDef:
    """
    Логическая группа для UI: один метод можно запускать в режиме
    `validate`, `correct` или `analyze`.
    """

    method_id: str
    title: str
    description: str
    validate_scope_id: str
    correct_scope_id: str | None

    def actions(self) -> dict[str, str | None]:
        # Сейчас `analyze` не применяет фиксы, но запускает те же чекеры,
        # что и `validate` (чтобы метод было чем тестировать).
        return {
            "validate": self.validate_scope_id,
            "correct": self.correct_scope_id,
            "analyze": self.validate_scope_id,
        }


METHODS: list[MethodDef] = [
    MethodDef(
        method_id="all_key",
        title="Все ключевые проверки",
        description="Валидация: шрифты/поля/структура/подписи/формулы/листинги. Коррекция: поля/нумерация и шрифты.",
        validate_scope_id="validate_all_key",
        correct_scope_id="correct_all",
    ),
    MethodDef(
        method_id="font",
        title="Шрифты",
        description="Проверка параметров шрифта основного текста и листингов + возможная коррекция шрифтов.",
        validate_scope_id="validate_font",
        correct_scope_id="correct_font",
    ),
    MethodDef(
        method_id="page",
        title="Поля/нумерация",
        description="Проверка полей страницы и нумерации PAGE (в footer).",
        validate_scope_id="validate_page",
        correct_scope_id="correct_page",
    ),
    MethodDef(
        method_id="structure",
        title="Структура",
        description="Проверка наличия обязательных структурных элементов.",
        validate_scope_id="validate_structure",
        correct_scope_id=None,
    ),
    MethodDef(
        method_id="table_caption",
        title="Подписи таблиц",
        description='Проверка формата подписи "Таблица N — Наименование".',
        validate_scope_id="validate_tables",
        correct_scope_id=None,
    ),
    MethodDef(
        method_id="formula_format",
        title="Формулы",
        description="Проверка простого выравнивания и номера в скобках для формул.",
        validate_scope_id="validate_formulas",
        correct_scope_id=None,
    ),
    MethodDef(
        method_id="listing_format",
        title="Листинги",
        description="Проверка шрифта/размера/интервалов/отступов в листингах (эвристика по моноширинному шрифту).",
        validate_scope_id="validate_listings",
        correct_scope_id=None,
    ),
    MethodDef(
        method_id="list_marker",
        title="Списки",
        description="Проверка и исправление маркеров ненумерованных и нумерации нумерованных списков.",
        validate_scope_id="validate_lists",
        correct_scope_id="correct_lists",
    ),
    MethodDef(
        method_id="figure_caption",
        title="Подписи рисунков",
        description='Проверка и исправление формата подписи «Рисунок N — Наименование».',
        validate_scope_id="validate_figures",
        correct_scope_id="correct_figures",
    ),
]


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (
        "<h3>Backend запущен.</h3>"
        "<p>Запусти фронтенд отдельно и открой:</p>"
        "<p><code>http://127.0.0.1:3000/</code></p>"
    )


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "backend": "gostchecker",
        "profiles": ["LIGHT", "MEDIUM", "HARD", "CUSTOM"],
        "checkers": len(CHECKER_MAP),
        "fixers": len(FIXER_MAP),
    }


@app.get("/api/modules")
def modules() -> dict[str, Any]:
    # Фронтенду важно: scope можно запускать и в validate, и в correct (по action).
    return {
        "scopes": [
            {
                "scope_id": s.scope_id,
                "title": s.title,
                "description": s.description,
                "checkers": s.checkers,
                "fixers": s.fixers,
            }
            for s in SCOPES
        ],
        "title_page_keywords": {
            "work_type": TITLE_PAGE_WORK_TYPE_VARIANTS,
            "university": TITLE_PAGE_UNIVERSITY_VARIANTS,
            "department": TITLE_PAGE_DEPARTMENT_VARIANTS,
            "author_markers": TITLE_PAGE_AUTHOR_MARKERS,
            "city_year_patterns": TITLE_PAGE_CITY_YEAR_PATTERNS,
            "report_markers": TITLE_PAGE_REPORT_MARKERS,
        },
        "checker_catalog": [
            {"checker_id": cid, "title_ru": CHECKER_TITLES_RU.get(cid, cid)}
            for cid in CHECKER_MAP.keys()
        ],
        "doc_classes": [
            {"class_id": cid, "title_ru": title}
            for cid, title in ALL_DOC_CLASS_CHOICES
        ],
    }


@app.get("/api/methods")
def methods() -> dict[str, Any]:
    return {
        "methods": [
            {
                "method_id": m.method_id,
                "title": m.title,
                "description": m.description,
                "actions": m.actions(),
            }
            for m in METHODS
        ],
        "profiles": [
            {"id": "LIGHT", "title_ru": "LIGHT"},
            {"id": "MEDIUM", "title_ru": "MEDIUM"},
            {"id": "HARD", "title_ru": "HARD"},
            {"id": "CUSTOM", "title_ru": "Custom"},
        ],
    }


@app.post("/api/classify")
def classify(file: UploadFile = File(...)) -> JSONResponse:
    data = file.file.read()
    document = DocumentModel.from_docx_bytes(data)
    info = DocumentTypeDetector().detect(document)
    return JSONResponse(content=info)


def _select_checker_ids(
    base_checker_ids: list[str],
    *,
    detected_doc_type: dict[str, Any],
    profile: str | None,
    custom_checks: list[str],
) -> list[str]:
    result = list(base_checker_ids)
    class_id = str(detected_doc_type.get("class_id") or "")
    selected_profile = (profile or "").upper()
    if selected_profile in PROFILE_CHECKERS:
        allowed = set(PROFILE_CHECKERS[selected_profile])
        result = [cid for cid in result if cid in allowed]
    elif selected_profile == "CUSTOM" and custom_checks:
        allowed = set(custom_checks)
        result = [cid for cid in result if cid in allowed]

    # Ограничения по классу документа для не-CUSTOM режимов.
    if selected_profile != "CUSTOM":
        disabled = set(detected_doc_type.get("disabled_checks") or [])
        if disabled:
            result = [cid for cid in result if cid not in disabled]
        if class_id == "REVIEW":
            review_only = {"margins", "font_family", "font_size", "font_style", "font_spacing"}
            result = [cid for cid in result if cid in review_only]

    return result


def _resolve_doc_type(data: bytes, doc_class_override: str | None) -> dict[str, Any]:
    document = DocumentModel.from_docx_bytes(data)
    detected = DocumentTypeDetector().detect(document)
    if doc_class_override and doc_class_override in DOC_CLASS_BY_ID:
        cls = DOC_CLASS_BY_ID[doc_class_override]
        detected = {
            **detected,
            "detected": True,
            "class_id": cls.class_id,
            "title_ru": cls.title_ru,
            "recommended_mode": cls.recommended_mode,
            "forced_mode": cls.forced_mode,
            "warning": cls.warning,
            "disabled_checks": list(cls.disabled_checks),
            "manual_override": True,
        }
    return detected


def _parse_custom_checks(custom_checks: str | None) -> list[str]:
    if not custom_checks:
        return []
    return [x.strip() for x in custom_checks.split(",") if x.strip()]


def _resolve_profile(profile: str | None, doc_type: dict[str, Any]) -> str | None:
    selected_profile = (profile or "").upper() or None
    forced = doc_type.get("forced_mode")
    if forced:
        return str(forced).upper()
    if selected_profile:
        return selected_profile
    if doc_type.get("recommended_mode"):
        return str(doc_type["recommended_mode"]).upper()
    return None


def _build_docx_preview(docx_bytes: bytes, *, per_page: int = 14, max_pages: int = 8) -> dict[str, Any]:
    try:
        document = DocumentModel.from_docx_bytes(docx_bytes)
    except Exception as exc:
        return {
            "pages": [],
            "paragraph_count": 0,
            "truncated": False,
            "error": f"Не удалось собрать preview: {exc}",
        }

    paragraphs = [
        (p.text or "").strip()
        for p in document.paragraphs
        if (p.text or "").strip()
    ]
    limited = paragraphs[: per_page * max_pages]
    pages = [
        {"page": index + 1, "paragraphs": limited[index * per_page : (index + 1) * per_page]}
        for index in range((len(limited) + per_page - 1) // per_page)
    ]
    return {
        "pages": pages,
        "paragraph_count": len(paragraphs),
        "truncated": len(paragraphs) > len(limited),
    }


def _serialize_run_context(
    doc_type: dict[str, Any],
    profile: str | None,
    checker_ids: list[str],
) -> dict[str, Any]:
    return {
        "document_type": doc_type,
        "profile": profile,
        "checker_ids": checker_ids,
    }


@app.post("/api/run")
def run(
    mode: str,
    scope_id: str,
    profile: str | None = None,
    custom_checks: str | None = None,
    doc_class_override: str | None = None,
    file: UploadFile = File(...),
) -> JSONResponse:
    if mode not in {"validate", "correct", "analyze"}:
        return JSONResponse(status_code=400, content={"error": "Unknown mode"})
    if scope_id not in SCOPE_INDEX:
        return JSONResponse(status_code=400, content={"error": "Unknown scope_id"})

    s = SCOPE_INDEX[scope_id]
    data = file.file.read()
    doc_type = _resolve_doc_type(data, doc_class_override=doc_class_override)
    selected_profile = _resolve_profile(profile, doc_type)
    custom_check_ids = _parse_custom_checks(custom_checks)

    # Собираем чекеры и фиксы.
    checker_ids = _select_checker_ids(
        s.checkers,
        detected_doc_type=doc_type,
        profile=selected_profile,
        custom_checks=custom_check_ids,
    )
    checkers = [CHECKER_MAP[cid] for cid in checker_ids if cid in CHECKER_MAP]

    validator = Validator(checkers=checkers)

    fixer = None
    auto_fix = False
    if mode == "correct":
        fixer_list = [FIXER_MAP[fid] for fid in s.fixers if fid in FIXER_MAP]
        fixer = Fixer(fixers=fixer_list)
        auto_fix = True

    engine = DocumentEngine(
        validator=validator,
        fixer=fixer,
        report_builder=JsonReportBuilder(),
        config=DocumentEngineConfig(auto_fix=auto_fix),
    )

    result = engine.process_docx_bytes(data, input_filename=file.filename)
    report = result.report
    report["run_context"] = _serialize_run_context(doc_type, selected_profile, checker_ids)

    violations_before = report.get("violations") or []
    violations_after = report.get("violations_after")
    violations_after = violations_after or []

    # Метрика “процент корректности” (эвристика):
    # чем меньше нарушений — тем выше процент.
    before_n = len(violations_before)
    after_n = len(violations_after)
    correctness_before = max(0, 100 - min(before_n, 40) * 2.5)
    correctness_after = max(0, 100 - min(after_n, 40) * 2.5)

    improvement = None
    if mode == "correct":
        if before_n == 0:
            improvement = 100
        else:
            improvement = max(0, min(100, int((before_n - after_n) / max(1, before_n) * 100)))

    help_summary = _build_help_summary(violations_before)

    fixed_payload: dict[str, Any] | None = None
    if mode == "correct" and result.fixed_docx_bytes:
        orig = file.filename or "document.docx"
        stem = orig.rsplit(".", 1)[0] if "." in orig else orig
        fixed_name = f"{stem}_fixed.docx"
        fixed_payload = {
            "filename": fixed_name,
            "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "size_bytes": len(result.fixed_docx_bytes),
            "base64": base64.b64encode(result.fixed_docx_bytes).decode("ascii"),
            "preview": _build_docx_preview(result.fixed_docx_bytes),
        }

    return JSONResponse(
        content={
            "mode": mode,
            "scope_id": scope_id,
            "report": report,
            "metrics": {
                "correctness_before_percent": correctness_before,
                "correctness_after_percent": correctness_after if mode == "correct" else None,
                "improvement_percent": improvement,
                "violations_before_count": before_n,
                "violations_after_count": after_n if mode == "correct" else None,
            },
            "help": help_summary,
            "fixed_file": fixed_payload,
            "document_type": doc_type,
            "profile": selected_profile,
            "checker_ids": checker_ids,
        }
    )


def _short(text: str, limit: int = 180) -> str:
    text = (text or "").strip().replace("\n", " ")
    if len(text) <= limit:
        return text
    return text[:limit] + "…"


def _build_help_summary(violations: list[dict[str, Any]]) -> dict[str, Any]:
    if not violations:
        return {"summary": "Ошибки не найдены", "items": []}

    items: list[dict[str, Any]] = []
    for v in violations:
        items.append(
            {
                "code": v.get("code"),
                "message": v.get("message"),
                "element_id": v.get("element_id"),
                "expected": v.get("expected"),
                "actual": v.get("actual"),
                "actual_text": _short(v.get("actual_text") or ""),
                "zone_type": v.get("zone_type"),
                "severity": v.get("severity"),
                "rule_ref": v.get("rule_ref"),
            }
        )

    # Группировка по коду для быстрого просмотра.
    by_code: dict[str, int] = {}
    for it in items:
        by_code[it["code"]] = by_code.get(it["code"], 0) + 1

    top_codes = sorted(by_code.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "summary": f"Найдено нарушений: {len(violations)}",
        "top_codes": [{"code": c, "count": n} for c, n in top_codes],
        "items": items,
    }

