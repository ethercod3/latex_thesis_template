"""Rich-рендеринг результатов проверки состояния проекта."""

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


def print_report(project_items: list[Check], console: Console | None = None) -> None:
    console = console or Console()
    warnings = [item for item in project_items if item.ok and item.warning]

    console.print("Проверка состояния проекта", style="bold")
    print_group(console, "Состояние проекта", project_items)

    if warnings:
        console.print(f"\nПроект можно использовать, но проверок с предупреждениями: {len(warnings)}.", style="yellow")
        return

    console.print("\nСостояние проекта корректно.", style="green")
