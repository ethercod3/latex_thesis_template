"""Проверки окружения и состояния проекта."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from common import ENV_PATH, PROJECT_DIR, command_path, env_value

from .models import Check


def configure_output_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


configure_output_encoding()


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
    path = command_path(command)
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
    path = command_path(command)
    if path is None:
        return Check(name=name, ok=False, required=required, detail=f"команда не найдена: {command}", fix=fix)

    return Check(name=name, ok=True, required=required, detail=path, fix=fix)


def warning_check(name: str, detail: str, fix: str) -> Check:
    return Check(name=name, ok=True, required=True, warning=True, detail=detail, fix=fix)


def ok_check(name: str, detail: str) -> Check:
    return Check(name=name, ok=True, required=True, detail=detail, fix="")


def safe_env_value(name: str) -> str | None:
    try:
        return env_value(name)
    except ModuleNotFoundError:
        return None


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
        shown = ", ".join(missing[:5])
        if len(missing) > 5:
            shown += f", ... (всего {len(missing)})"
        return [warning_check(name, f"нет PDF: {shown}", "Пересоберите диаграммы через task diagrams или task build.")]

    if stale:
        shown = ", ".join(stale[:5])
        if len(stale) > 5:
            shown += f", ... (всего {len(stale)})"
        return [
            warning_check(
                name, f"PDF старее исходников: {shown}", "Пересоберите диаграммы через task diagrams или task build."
            )
        ]

    return [ok_check(name, f"проверено файлов: {len(source_files)}")]


def project_state_checks() -> list[Check]:
    items: list[Check] = []

    if ENV_PATH.is_file():
        items.append(ok_check(".env", ".env найден"))
    else:
        items.append(warning_check(".env", ".env не найден", "Создайте .env по примеру .env.example."))

    target = safe_env_value("TARGET")
    if not target:
        items.append(warning_check("TARGET", "TARGET не задан в .env", "Укажите TARGET в .env."))
    else:
        target_path = PROJECT_DIR / target
        if target_path.is_file():
            items.append(ok_check("TARGET", f"{target} найден"))
        else:
            items.append(warning_check("TARGET", f"файл не найден: {target}", "Проверьте TARGET в .env."))

    vault_path = safe_env_value("VAULT_OS_PATH")
    if not vault_path:
        items.append(warning_check("VAULT_OS_PATH", "VAULT_OS_PATH не задан в .env", "Укажите путь к проекту с кодом."))
    else:
        path = (PROJECT_DIR / vault_path).resolve()
        if path.exists():
            items.append(ok_check("VAULT_OS_PATH", f"{vault_path} найден"))
        else:
            items.append(
                warning_check(
                    "VAULT_OS_PATH",
                    f"путь не найден: {vault_path}",
                    "Проверьте VAULT_OS_PATH в .env или положите код по ожидаемому пути.",
                )
            )

    for pdf_name in ("титульник.pdf", "задание.pdf"):
        if (PROJECT_DIR / pdf_name).is_file():
            items.append(ok_check(pdf_name, f"{pdf_name} найден"))
        else:
            items.append(
                warning_check(
                    pdf_name,
                    f"{pdf_name} не найден",
                    "Сгенерируйте титульные страницы через task docx или task build.",
                )
            )

    items.extend(diagram_state_checks("Mermaid-диаграммы", PROJECT_DIR / "mermaid", ("*.mmd", "*.mermaid", "*.mmdc")))
    items.extend(diagram_state_checks("Python-диаграммы", PROJECT_DIR / "python_diagrams", "*.py"))
    return items


def uv_environment_check() -> Check:
    if command_path("uv") is None:
        return Check(
            name="uv",
            ok=False,
            required=True,
            detail="команда не найдена: uv",
            fix="Установите uv: https://docs.astral.sh/uv/",
        )

    result = run(["uv", "sync", "--check"], timeout=120)
    if result is None:
        return Check(
            name="uv environment",
            ok=False,
            required=True,
            detail="проверка uv sync --check не завершилась",
            fix="Синхронизируйте окружение через: uv sync",
        )

    if result.returncode != 0:
        detail = "окружение uv не синхронизировано"
        first = first_line(result.stdout)
        if first:
            detail += f": {first}"
        return Check(
            name="uv environment",
            ok=False,
            required=True,
            detail=detail,
            fix="Синхронизируйте окружение через: uv sync",
        )

    return Check(
        name="uv environment",
        ok=True,
        required=True,
        detail="окружение синхронизировано",
        fix="Синхронизируйте окружение через: uv sync",
    )


def docker_compose_check() -> Check:
    if command_path("docker") is None:
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


def pyluatex_check(*, required: bool) -> Check:
    if command_path("kpsewhich") is None:
        return Check(
            name="Пакет PyLuaTeX",
            ok=False,
            required=required,
            detail="команда kpsewhich не найдена, невозможно найти pyluatex.sty",
            fix="Установите TeX Live или MiKTeX с пакетом pyluatex.",
        )

    result = run(["kpsewhich", "pyluatex.sty"])
    path = first_line(result.stdout if result else "")
    if result is None or result.returncode != 0 or not path:
        return Check(
            name="Пакет PyLuaTeX",
            ok=False,
            required=required,
            detail="kpsewhich не нашел pyluatex.sty",
            fix="Установите TeX-пакет pyluatex или обновите базу имен файлов TeX.",
        )

    return Check(
        name="Пакет PyLuaTeX",
        ok=True,
        required=required,
        detail=path,
        fix="Установите TeX-пакет pyluatex или обновите базу имен файлов TeX.",
    )


def checks() -> list[Check]:
    return [
        command_check(
            "Task", "task", ["task", "--version"], required=True, fix="Установите Task: https://taskfile.dev/"
        ),
        command_check("Git", "git", ["git", "--version"], required=True, fix="Установите Git и добавьте его в PATH."),
        command_check("uv", "uv", ["uv", "--version"], required=True, fix="Установите uv: https://docs.astral.sh/uv/"),
        command_check("Docker", "docker", ["docker", "--version"], required=True, fix="Установите Docker Desktop."),
        docker_compose_check(),
        command_check(
            "LuaLaTeX",
            "lualatex",
            ["lualatex", "--version"],
            required=False,
            fix="Установите TeX Live или MiKTeX, если нужна локальная сборка без Docker.",
        ),
        command_check(
            "latexmk",
            "latexmk",
            ["latexmk", "--version"],
            required=False,
            fix="Установите latexmk, если нужна локальная сборка без Docker. Обычно он входит в TeX Live.",
        ),
        command_check(
            "biber",
            "biber",
            ["biber", "--version"],
            required=False,
            fix="Установите biber, если нужна локальная сборка без Docker. Обычно он входит в TeX Live.",
        ),
        command_check(
            "kpsewhich",
            "kpsewhich",
            ["kpsewhich", "--version"],
            required=False,
            fix="Установите TeX Live или MiKTeX, если нужна локальная сборка без Docker.",
        ),
        pyluatex_check(required=False),
        command_check(
            "Mermaid CLI",
            "mmdc",
            ["mmdc", "--version"],
            required=False,
            fix="Установите @mermaid-js/mermaid-cli или используйте task mermaid:docker.",
        ),
        command_check(
            "pdfcrop",
            "pdfcrop",
            ["pdfcrop", "--version"],
            required=False,
            fix="Установите pdfcrop из TeX Live/MiKTeX, используйте task mermaid -- --no-crop или task mermaid:docker.",
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
