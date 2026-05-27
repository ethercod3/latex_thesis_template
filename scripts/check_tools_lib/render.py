"""Rich-рендеринг результатов проверки окружения."""

from __future__ import annotations

from rich.console import Console
from rich.text import Text

from .models import Check


def status_text(check: Check) -> Text:
    if check.ok and check.warning:
        return Text("WARN", style="yellow")
    if check.ok:
        return Text("OK", style="green")
    if check.required:
        return Text("MISS", style="red")
    return Text("SKIP", style="yellow")


def print_group(console: Console, title: str, items: list[Check]) -> None:
    console.print()
    console.print(title, style="bold")
    for item in items:
        line = Text("  [")
        line.append_text(status_text(item))
        line.append("] ")
        line.append(item.name)
        line.append(": ")
        line.append(item.detail)
        console.print(line)
        if not item.ok or item.warning:
            console.print(f"        Как исправить: {item.fix}")


def print_report(items: list[Check], project_items: list[Check], console: Console | None = None) -> None:
    console = console or Console()
    required = [item for item in items if item.required]
    optional = [item for item in items if not item.required]
    missing_required = [item for item in required if not item.ok]
    warnings = [item for item in [*items, *project_items] if item.ok and item.warning]

    console.print("Проверка окружения проекта", style="bold")
    print_group(console, "Обязательные инструменты для поддерживаемой сборки", required)
    print_group(console, "Состояние проекта", project_items)
    print_group(console, "Опциональные локальные инструменты", optional)

    if missing_required:
        console.print(f"\nОкружение не готово: обязательных проверок с ошибкой: {len(missing_required)}.", style="red")
        return

    if warnings:
        console.print(
            f"\nОкружение можно использовать, но проверок с предупреждениями: {len(warnings)}.", style="yellow"
        )
        return

    console.print("\nОкружение готово.", style="green")
