from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Protocol

from engine.models.document_model import DocumentModel
from engine.models.violation_model import Violation
from engine.models.zone_model import Zone, ZoneType


class BaseChecker(Protocol):
    """Интерфейс checker-а: анализирует документ и возвращает нарушения."""

    def supported_zones(self) -> set[ZoneType]:  # pragma: no cover
        ...

    def run(self, document: DocumentModel, zones: list[Zone]) -> list[Violation]:  # pragma: no cover
        ...


@dataclass(frozen=True)
class ValidatorConfig:
    enabled_checker_ids: set[str] | None = None


@dataclass
class Validator:
    """
    Валидатор оркестрирует набор checker-ов и агрегирует нарушения.
    """

    checkers: list[BaseChecker]
    config: ValidatorConfig = field(default_factory=ValidatorConfig)

    def validate(self, document: DocumentModel, zones: list[Zone]) -> list[Violation]:
        violations: list[Violation] = []

        for checker in self.checkers:
            supported = set(checker.supported_zones())
            relevant_zones = [z for z in zones if z.zone_type in supported]
            if not relevant_zones:
                continue

            try:
                violations.extend(checker.run(document, relevant_zones))
            except Exception as e:  # pragma: no cover
                raise RuntimeError(f"Checker {checker.__class__.__name__} failed: {e}") from e

        # Дедупликация: code + element_id
        uniq: dict[tuple[str, str], Violation] = {}
        for v in violations:
            uniq[(v.code, v.element_id)] = v
        return list(uniq.values())

