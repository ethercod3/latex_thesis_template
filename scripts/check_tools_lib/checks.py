"""Проверки состояния проекта."""

from __future__ import annotations

from pathlib import Path
import sys

from common import ENV_PATH, PROJECT_DIR, env_value

from .models import Check


def configure_output_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


configure_output_encoding()


def warning_check(name: str, detail: str, fix: str) -> Check:
    return Check(name=name, ok=True, required=True, warning=True, detail=detail, fix=fix)


def ok_check(name: str, detail: str) -> Check:
    return Check(name=name, ok=True, required=True, detail=detail, fix="")


def state_check(name: str, ok: bool, ok_detail: str, missing_detail: str, fix: str) -> Check:
    return ok_check(name, ok_detail) if ok else warning_check(name, missing_detail, fix)


def safe_env_value(name: str) -> str | None:
    try:
        return env_value(name)
    except ModuleNotFoundError:
        return None


def shown_paths(paths: list[str], limit: int = 5) -> str:
    shown = ", ".join(paths[:limit])
    if len(paths) > limit:
        shown += f", ... (всего {len(paths)})"
    return shown


def diagram_state_checks(name: str, source_dir: Path, patterns: str | tuple[str, ...]) -> list[Check]:
    if not source_dir.is_dir():
        return [
            warning_check(
                name, f"папка не найдена: {source_dir.relative_to(PROJECT_DIR)}", "Проверьте структуру проекта."
            )
        ]

    missing: list[str] = []
    stale: list[str] = []
    if isinstance(patterns, str):
        patterns = (patterns,)
    source_files = sorted({source for pattern in patterns for source in source_dir.glob(pattern)})
    for source in source_files:
        output = PROJECT_DIR / "figures" / f"{source.stem}.pdf"
        if not output.is_file():
            missing.append(output.relative_to(PROJECT_DIR).as_posix())
        elif output.stat().st_mtime < source.stat().st_mtime:
            stale.append(output.relative_to(PROJECT_DIR).as_posix())

    if missing:
        return [
            warning_check(
                name, f"нет PDF: {shown_paths(missing)}", "Пересоберите диаграммы через task diagrams или task build."
            )
        ]

    if stale:
        return [
            warning_check(
                name,
                f"PDF старее исходников: {shown_paths(stale)}",
                "Пересоберите диаграммы через task diagrams или task build.",
            )
        ]

    return [ok_check(name, f"проверено файлов: {len(source_files)}")]


def project_state_checks() -> list[Check]:
    items = [
        state_check(
            ".env", ENV_PATH.is_file(), ".env найден", ".env не найден", "Создайте .env по примеру .env.example."
        )
    ]

    target = safe_env_value("TARGET")
    if not target:
        items.append(warning_check("TARGET", "TARGET не задан в .env", "Укажите TARGET в .env."))
    else:
        items.append(
            state_check(
                "TARGET",
                (PROJECT_DIR / target).is_file(),
                f"{target} найден",
                f"файл не найден: {target}",
                "Проверьте TARGET в .env.",
            )
        )

    project_source_path = safe_env_value("PROJECT_SOURCE_OS_PATH")
    if project_source_path:
        items.append(
            state_check(
                "PROJECT_SOURCE_OS_PATH",
                (PROJECT_DIR / project_source_path).resolve().exists(),
                f"{project_source_path} найден",
                f"путь не найден: {project_source_path}",
                "Проверьте PROJECT_SOURCE_OS_PATH в .env или положите код по ожидаемому пути.",
            )
        )

    items.extend(diagram_state_checks("Mermaid-диаграммы", PROJECT_DIR / "mermaid", ("*.mmd", "*.mermaid", "*.mmdc")))
    items.extend(diagram_state_checks("Python-диаграммы", PROJECT_DIR / "python_diagrams", "*.py"))
    return items


def checks() -> list[Check]:
    return project_state_checks()
