from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    required: bool
    detail: str
    fix: str
    warning: bool = False
