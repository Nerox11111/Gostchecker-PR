from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from engine.models.violation_model import FixOperation, Violation


class BaseReportBuilder(Protocol):
    def build_json(
        self,
        violations: list[Violation],
        applied_fixes: list[FixOperation],
        violations_after: list[Violation] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:  # pragma: no cover
        ...


@dataclass
class JsonReportBuilder:
    def build_json(
        self,
        violations: list[Violation],
        applied_fixes: list[FixOperation],
        violations_after: list[Violation] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        extra = extra or {}
        return {
            "violations": [v.to_dict() for v in violations],
            "applied_fixes": [op.to_dict() for op in applied_fixes],
            "violations_after": [v.to_dict() for v in violations_after] if violations_after is not None else None,
            **extra,
        }

