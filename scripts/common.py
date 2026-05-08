from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


PROJECT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_DIR / ".env"


def env_value(name: str) -> str | None:
    if not ENV_PATH.exists():
        return None

    from dotenv import dotenv_values

    value = dotenv_values(ENV_PATH).get(name)
    return value if value else None


def require_command(command: str) -> None:
    if shutil.which(command) is None:
        raise RuntimeError(
            f"Не найдена команда '{command}'. Установите нужную программу и убедитесь, "
            "что она доступна в терминале."
        )


def run_command(
    command: list[str],
    *,
    check: bool = True,
    cwd: Path = PROJECT_DIR,
) -> subprocess.CompletedProcess[str]:
    print(f"==> {' '.join(command)}", flush=True)
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        text=True,
        stdout=None,
        stderr=None,
    )
