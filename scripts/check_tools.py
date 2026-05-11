from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys

from common import PROJECT_DIR

REQUIREMENTS_PATH = PROJECT_DIR / "requirements.txt"


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    required: bool
    detail: str
    fix: str
    warning: bool = False


class Style:
    def __init__(self) -> None:
        enabled = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
        self.green = "\033[32m" if enabled else ""
        self.yellow = "\033[33m" if enabled else ""
        self.red = "\033[31m" if enabled else ""
        self.bold = "\033[1m" if enabled else ""
        self.reset = "\033[0m" if enabled else ""


STYLE = Style()


def run(command: list[str], timeout: int = 10) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            command,
            cwd=PROJECT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def first_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("Initial Win CP", "I changed them", "Reverting Windows console")):
            return stripped
    return ""


def command_check(
    name: str,
    command: str,
    version_command: list[str],
    *,
    required: bool,
    fix: str,
    timeout: int = 10,
) -> Check:
    path = shutil.which(command)
    if path is None:
        return Check(name=name, ok=False, required=required, detail=f"команда не найдена: {command}", fix=fix)

    result = run(version_command, timeout=timeout)
    if result is None:
        if not required:
            return Check(name=name, ok=True, required=required, detail=f"{path}; проверка версии недоступна", fix=fix)
        return Check(
            name=name,
            ok=True,
            required=required,
            warning=True,
            detail=f"{path}; проверка версии завершилась с ошибкой",
            fix=fix,
        )

    version = first_line(result.stdout)
    if result.returncode != 0:
        detail = f"{path}; команда проверки версии завершилась с кодом {result.returncode}"
        if version:
            detail += f": {version}"
        if not required:
            return Check(name=name, ok=True, required=required, detail=detail, fix=fix)
        return Check(name=name, ok=True, required=required, warning=True, detail=detail, fix=fix)

    detail = f"{path}"
    if version:
        detail += f"; {version}"
    return Check(name=name, ok=True, required=required, detail=detail, fix=fix)


def path_only_check(name: str, command: str, *, required: bool, fix: str) -> Check:
    path = shutil.which(command)
    if path is None:
        return Check(name=name, ok=False, required=required, detail=f"команда не найдена: {command}", fix=fix)

    return Check(name=name, ok=True, required=required, detail=path, fix=fix)


def python_check() -> Check:
    path = shutil.which("python")
    if path is None:
        return Check(
            name="Python",
            ok=False,
            required=True,
            detail="команда не найдена: python",
            fix="Установите Python 3.13+ и убедитесь, что команда python доступна в PATH.",
        )

    result = run(["python", "--version"])
    version = first_line(result.stdout if result else "")
    warning = False
    detail = f"{path}"
    if version:
        detail += f"; {version}"
        match = re.search(r"Python\s+(\d+)\.(\d+)", version)
        if match and (int(match.group(1)), int(match.group(2))) < (3, 13):
            warning = True
            detail += "; инструменты проекта настроены на Python 3.13+"

    return Check(
        name="Python",
        ok=True,
        required=True,
        warning=warning,
        detail=detail,
        fix="Установите Python 3.13+ и убедитесь, что команда python доступна в PATH.",
    )


def docker_compose_check() -> Check:
    if shutil.which("docker") is None:
        return Check(
            name="Docker Compose plugin",
            ok=False,
            required=True,
            detail="команда docker не найдена",
            fix="Установите Docker Desktop, затем проверьте: docker compose version.",
        )

    result = run(["docker", "compose", "version"], timeout=20)
    if result is None or result.returncode != 0:
        detail = "команда docker compose version завершилась с ошибкой"
        if result and first_line(result.stdout):
            detail += f": {first_line(result.stdout)}"
        return Check(
            name="Docker Compose plugin",
            ok=False,
            required=True,
            detail=detail,
            fix="Установите или включите плагин Docker Compose в Docker Desktop.",
        )

    return Check(
        name="Docker Compose plugin",
        ok=True,
        required=True,
        detail=first_line(result.stdout),
        fix="Установите или включите плагин Docker Compose в Docker Desktop.",
    )


def pyluatex_check() -> Check:
    if shutil.which("kpsewhich") is None:
        return Check(
            name="Пакет PyLuaTeX",
            ok=False,
            required=True,
            detail="команда kpsewhich не найдена, невозможно найти pyluatex.sty",
            fix="Установите TeX Live или MiKTeX с пакетом pyluatex.",
        )

    result = run(["kpsewhich", "pyluatex.sty"])
    path = first_line(result.stdout if result else "")
    if result is None or result.returncode != 0 or not path:
        return Check(
            name="Пакет PyLuaTeX",
            ok=False,
            required=True,
            detail="kpsewhich не нашел pyluatex.sty",
            fix="Установите TeX-пакет pyluatex или обновите базу имен файлов TeX.",
        )

    return Check(
        name="Пакет PyLuaTeX",
        ok=True,
        required=True,
        detail=path,
        fix="Установите TeX-пакет pyluatex или обновите базу имен файлов TeX.",
    )


def requirements_check() -> Check:
    if not REQUIREMENTS_PATH.is_file():
        return Check(
            name="Python-пакеты",
            ok=False,
            required=True,
            detail="requirements.txt не найден",
            fix="Восстановите requirements.txt.",
        )

    missing: list[str] = []
    for line in REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines():
        package = line.strip()
        if not package or package.startswith("#"):
            continue
        package = re.split(r"[<>=!~]", package, maxsplit=1)[0].strip()
        if not package:
            continue
        try:
            metadata.version(package)
        except metadata.PackageNotFoundError:
            missing.append(package)

    if missing:
        shown = ", ".join(missing[:8])
        if len(missing) > 8:
            shown += f", ... (всего {len(missing)})"
        return Check(
            name="Python-пакеты",
            ok=False,
            required=True,
            detail=f"не установлены пакеты: {shown}",
            fix="Запустите: task deps",
        )

    return Check(
        name="Python-пакеты",
        ok=True,
        required=True,
        detail="все пакеты из requirements.txt установлены",
        fix="Запустите: task deps",
    )


def checks() -> list[Check]:
    return [
        command_check(
            "Task", "task", ["task", "--version"], required=True, fix="Установите Task: https://taskfile.dev/"
        ),
        command_check("Git", "git", ["git", "--version"], required=True, fix="Установите Git и добавьте его в PATH."),
        python_check(),
        requirements_check(),
        command_check("Docker", "docker", ["docker", "--version"], required=True, fix="Установите Docker Desktop."),
        docker_compose_check(),
        command_check(
            "LuaLaTeX",
            "lualatex",
            ["lualatex", "--version"],
            required=True,
            fix="Установите TeX Live или MiKTeX и добавьте TeX binaries в PATH.",
        ),
        command_check(
            "latexmk",
            "latexmk",
            ["latexmk", "--version"],
            required=True,
            fix="Установите latexmk. Обычно он входит в TeX Live.",
        ),
        command_check(
            "biber",
            "biber",
            ["biber", "--version"],
            required=True,
            fix="Установите biber. Обычно он входит в TeX Live.",
        ),
        command_check(
            "kpsewhich",
            "kpsewhich",
            ["kpsewhich", "--version"],
            required=True,
            fix="Установите TeX Live или MiKTeX и добавьте TeX binaries в PATH.",
        ),
        pyluatex_check(),
        command_check(
            "Mermaid CLI",
            "mmdc",
            ["mmdc", "--version"],
            required=False,
            fix="Установите @mermaid-js/mermaid-cli или используйте task mermaid:docker.",
        ),
        command_check(
            "LibreOffice",
            "soffice",
            ["soffice", "--version"],
            required=False,
            fix="Установите LibreOffice/Microsoft Word или используйте Docker для конвертации DOCX.",
        ),
        command_check(
            "Ghostscript",
            "gs",
            ["gs", "--version"],
            required=False,
            fix="Установите Ghostscript или используйте Docker для конвертации DOCX.",
        ),
        command_check(
            "qpdf",
            "qpdf",
            ["qpdf", "--version"],
            required=False,
            fix="Установите qpdf или используйте Docker для конвертации DOCX.",
        ),
        path_only_check(
            "diff-pdf",
            "diff-pdf",
            required=False,
            fix="Установите diff-pdf, если нужно визуальное сравнение PDF.",
        ),
    ]


def status_label(check: Check) -> str:
    if check.ok and check.warning:
        return f"{STYLE.yellow}WARN{STYLE.reset}"
    if check.ok:
        return f"{STYLE.green}OK{STYLE.reset}"
    if check.required:
        return f"{STYLE.red}MISS{STYLE.reset}"
    return f"{STYLE.yellow}SKIP{STYLE.reset}"


def print_group(title: str, items: list[Check]) -> None:
    print(f"\n{STYLE.bold}{title}{STYLE.reset}")
    for item in items:
        print(f"  [{status_label(item)}] {item.name}: {item.detail}")
        if not item.ok or item.warning:
            print(f"        Как исправить: {item.fix}")


def main() -> int:
    items = checks()
    required = [item for item in items if item.required]
    optional = [item for item in items if not item.required]
    missing_required = [item for item in required if not item.ok]
    warnings = [item for item in items if item.ok and item.warning]

    print(f"{STYLE.bold}Проверка окружения проекта{STYLE.reset}")
    print_group("Обязательные инструменты для поддерживаемой сборки", required)
    print_group("Опциональные локальные инструменты", optional)

    if missing_required:
        print(
            f"\n{STYLE.red}Окружение не готово: обязательных проверок с ошибкой: {len(missing_required)}.{STYLE.reset}"
        )
        return 1

    if warnings:
        print(
            f"\n{STYLE.yellow}Окружение можно использовать, но проверок с предупреждениями: {len(warnings)}.{STYLE.reset}"
        )
        return 0

    print(f"\n{STYLE.green}Окружение готово.{STYLE.reset}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
