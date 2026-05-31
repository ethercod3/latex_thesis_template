"""CLI вход для диагностики состояния проекта."""

from __future__ import annotations

from rich.console import Console

from .checks import project_state_checks
from .render import print_report


def main() -> int:
    project_items = project_state_checks()
    print_report(project_items, Console())
    return 0
