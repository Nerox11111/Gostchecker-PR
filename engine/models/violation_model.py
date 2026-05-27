from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.models.zone_model import ZoneType


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class Violation:
    code: str
    element_id: str
    message: str
    expected: str | None = None
    actual: str | None = None
    actual_text: str | None = None
    zone_type: ZoneType | None = None
    severity: Severity = Severity.MEDIUM
    rule_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "element_id": self.element_id,
            "message": self.message,
            "expected": self.expected,
            "actual": self.actual,
            "actual_text": self.actual_text,
            "zone_type": self.zone_type.value if self.zone_type is not None else None,
            "severity": self.severity.value,
            "rule_ref": self.rule_ref,
        }


@dataclass(frozen=True)
class FixOperation:
    # Например: "SET_FONT", "SET_MARGINS", "REBUILD_TOC"
    action: str
    target_element_id: str | None = None
    value: str | None = None
    meta: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "target_element_id": self.target_element_id,
            "value": self.value,
            "meta": self.meta or {},
        }

