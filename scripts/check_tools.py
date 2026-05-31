"""Совместимый входной файл для проверки состояния проекта."""

from __future__ import annotations

from check_tools_lib import (
    Check,
    checks,
    diagram_state_checks,
    main,
    ok_check,
    project_state_checks,
    safe_env_value,
    warning_check,
)

__all__ = [
    "Check",
    "checks",
    "diagram_state_checks",
    "main",
    "ok_check",
    "project_state_checks",
    "safe_env_value",
    "warning_check",
]


if __name__ == "__main__":
    raise SystemExit(main())
