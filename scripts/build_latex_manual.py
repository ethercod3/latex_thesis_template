"""Локальная сборка диплома через установленный LaTeX toolchain.

Поддерживает сборку через latexmk и ручную цепочку LuaLaTeX/Biber, складывая
временные файлы в .aux_files и проверяя наличие внешних команд заранее.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import sys

from plumbum import local
import typer

from common import PROJECT_DIR, ScriptError, env_value

AUX_DIR = PROJECT_DIR / ".aux_files"


def target_tex_path(target_arg: str | None) -> Path:
    if target_arg:
        return (PROJECT_DIR / target_arg).resolve()

    target = env_value("TARGET")
    if target:
        return (PROJECT_DIR / target).resolve()

    tex_files = sorted(PROJECT_DIR.glob("*.tex"))
    if len(tex_files) == 1:
        return tex_files[0].resolve()

    raise ScriptError(
        "Не удалось понять, какой .tex-файл нужно собрать. "
        "Укажите TARGET в файле .env или передайте путь через --target."
    )


def lualatex_command(target: Path) -> list[str]:
    return [
        "lualatex",
        "--shell-escape",
        "-synctex=1",
        "-interaction=nonstopmode",
        "-output-directory=.aux_files",
        str(target.relative_to(PROJECT_DIR)),
    ]


def latexmk_command(target: Path) -> list[str]:
    return [
        "latexmk",
        str(target.relative_to(PROJECT_DIR)),
    ]


def output_pdf_path(target: Path) -> Path:
    return PROJECT_DIR / f"{target.stem}.pdf"


def run_external(command: list[str]) -> tuple[int, str, str]:
    print(f"==> {' '.join(command)}", flush=True)
    proc = local[command[0]]
    for arg in command[1:]:
        proc = proc[arg]
    proc = proc.with_cwd(PROJECT_DIR)
    return proc.run()


def build_with_latexmk(target: Path) -> Path:
    if not target.is_file():
        raise ScriptError(f"Указанный .tex-файл не найден: {target}")

    code, stdout, stderr = run_external(latexmk_command(target))
    if code != 0:
        details = (stderr or stdout).strip()
        raise ScriptError(f"latexmk завершился с ошибкой.\n{details}")

    output_pdf = output_pdf_path(target)
    if not output_pdf.is_file():
        raise ScriptError(
            f"PDF-файл не был создан там, где ожидалось: {output_pdf}. " "Проверьте сообщения latexmk выше."
        )

    return output_pdf


def build_without_latexmk(target: Path) -> Path:
    if not target.is_file():
        raise ScriptError(f"Указанный .tex-файл не найден: {target}")

    AUX_DIR.mkdir(exist_ok=True)
    for command in (
        lualatex_command(target),
        ["biber", str(AUX_DIR / f"{target.stem}.bcf")],
        lualatex_command(target),
        lualatex_command(target),
    ):
        code, stdout, stderr = run_external(command)
        if code != 0:
            details = (stderr or stdout).strip()
            raise ScriptError(f"Команда завершилась с ошибкой: {' '.join(command)}\n{details}")

    aux_pdf = AUX_DIR / f"{target.stem}.pdf"
    output_pdf = output_pdf_path(target)

    if not aux_pdf.is_file():
        raise ScriptError(f"PDF-файл не был создан там, где ожидалось: {aux_pdf}. " "Проверьте сообщения LaTeX выше.")

    shutil.copy2(aux_pdf, output_pdf)
    return output_pdf


def main(
    target: str | None = typer.Option(
        None,
        "--target",
        help="Путь к .tex-файлу. По умолчанию берется TARGET из .env.",
    ),
    no_latexmk: bool = typer.Option(
        False,
        "--no-latexmk",
        help="Не использовать latexmk. Запустить ручную цепочку: lualatex, biber, lualatex, lualatex.",
    ),
) -> None:
    try:
        target_path = target_tex_path(target)
        if no_latexmk:
            output_pdf = build_without_latexmk(target_path)
        else:
            output_pdf = build_with_latexmk(target_path)

        print(f"\nГотово: {output_pdf.relative_to(PROJECT_DIR)}")
    except ScriptError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
