from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SectionNode:
    element_id: str
    title: str
    level: int
    # Номер в формате "1", "1.1" и т.п.
    number_str: str | None = None
    children: list["SectionNode"] = field(default_factory=list)

