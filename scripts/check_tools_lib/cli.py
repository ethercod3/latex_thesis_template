"""CLI вход для диагностики окружения."""

from __future__ import annotations

from rich.console import Console

from .checks import checks, project_state_checks
from .render import print_report


def main() -> int:
    items = checks()
    project_items = project_state_checks()
    print_report(items, project_items, Console())
    required = [item for item in items if item.required]
    missing_required = [item for item in required if not item.ok]
    warnings = [item for item in [*items, *project_items] if item.ok and item.warning]
    if missing_required:
        return 1
    if warnings:
        return 0
    return 0
