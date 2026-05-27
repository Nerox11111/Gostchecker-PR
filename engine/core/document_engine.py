from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any

from engine.analyzers.structure_analyzer import StructureAnalyzer
from engine.analyzers.document_type_detector import DocumentTypeDetector
from engine.analyzers.zone_detector import ZoneDetector
from engine.core.fixer import Fixer
from engine.core.report_builder import BaseReportBuilder
from engine.core.validator import Validator
from engine.models.document_model import DocumentModel


@dataclass
class EngineResult:
    input_filename: str | None
    report: dict[str, Any]
    violations_before: list[Any]
    violations_after: list[Any] | None = None
    applied_fixes: list[Any] | None = None
    fixed_docx_bytes: bytes | None = None


@dataclass
class DocumentEngineConfig:
    auto_fix: bool = False


class DocumentEngine:
    """
    Главный управляющий модуль движка.
    На текущем этапе: сбор pipeline будет расширен по мере реализации парсера/зон/чекеров/фикcеров.
    """

    def __init__(
        self,
        validator: Validator,
        fixer: Fixer | None,
        report_builder: BaseReportBuilder,
        config: DocumentEngineConfig | None = None,
    ):
        self.validator = validator
        self.fixer = fixer
        self.report_builder = report_builder
        self.config = config or DocumentEngineConfig()

    def process_docx_bytes(
        self,
        docx_bytes: bytes,
        *,
        input_filename: str | None = None,
    ) -> EngineResult:
        # 1) Парсер
        document = DocumentModel.from_docx_bytes(docx_bytes)

        # Информация о типе документа (по титульным ключевым словам)
        doc_type = DocumentTypeDetector().detect(document)
        document.metadata["document_type"] = doc_type

        # 2) Зоны и структура
        ZoneDetector().detect_zones(document)
        StructureAnalyzer().analyze(document)

        # 3) Валидация
        violations_before = self.validator.validate(document, document.zones)

        applied_ops = None
        violations_after = None
        fixed_docx_bytes = None

        # 4) Исправления + повторная валидация
        if self.config.auto_fix and self.fixer is not None:
            operations = self.fixer.build_operations(document, violations_before)
            fixed_docx_bytes, applied_ops = self.fixer.apply_fixes(
                docx_bytes=docx_bytes,
                document=document,
                operations=operations,
            )

            # Повторная проверка.
            document_after = DocumentModel.from_docx_bytes(fixed_docx_bytes)
            ZoneDetector().detect_zones(document_after)
            StructureAnalyzer().analyze(document_after)
            violations_after = self.validator.validate(document_after, document_after.zones)

        report = self.report_builder.build_json(
            violations=violations_before,
            applied_fixes=applied_ops or [],
            violations_after=violations_after,
            extra={
                "input_filename": input_filename,
                "mode": "auto_fix" if self.config.auto_fix else "validate_only",
                "input_summary": document.to_dict_summary(),
                "document_type": doc_type,
            },
        )

        return EngineResult(
            input_filename=input_filename,
            report=report,
            violations_before=violations_before,
            violations_after=violations_after,
            applied_fixes=applied_ops,
            fixed_docx_bytes=fixed_docx_bytes,
        )

