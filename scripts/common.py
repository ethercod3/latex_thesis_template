from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
from collections.abc import Callable

PROJECT_DIR = Path.cwd().resolve() if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_DIR / ".env"


class ScriptError(RuntimeError):
    pass


def env_value(name: str) -> str | None:
    if not ENV_PATH.exists():
        return None

    from dotenv import dotenv_values

    value = dotenv_values(ENV_PATH).get(name)
    return value if value else None


def command_path(command: str) -> str | None:
    return shutil.which(command)


def command_exists(command: str) -> bool:
    return command_path(command) is not None


def require_command(command: str) -> None:
    if command_path(command) is None:
        raise ScriptError(
            f"Не найдена команда '{command}'. Установите нужную программу и убедитесь, " "что она доступна в терминале."
        )


def command_succeeds(command: list[str], *, cwd: Path = PROJECT_DIR) -> bool:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return False

    return result.returncode == 0


def capture_command(command: list[str], *, cwd: Path = PROJECT_DIR) -> str:
    return subprocess.check_output(command, cwd=cwd, text=True).strip()


def docker_compose_command() -> list[str]:
    if command_exists("docker") and command_succeeds(["docker", "compose", "version"]):
        return ["docker", "compose"]

    if command_exists("docker-compose"):
        return ["docker-compose"]

    raise ScriptError(
        "Не найден Docker Compose. Установите Docker Desktop или docker-compose и убедитесь, "
        "что команда доступна в терминале."
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


def script_main(main: Callable[[], int]) -> int:
    try:
        return main()
    except subprocess.CalledProcessError as error:
        print(
            f"Команда завершилась с ошибкой (код {error.returncode}): {' '.join(error.cmd)}",
            file=sys.stderr,
        )
        print("Проверьте сообщения выше: там обычно указана причина ошибки.", file=sys.stderr)
        return error.returncode
    except RuntimeError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
