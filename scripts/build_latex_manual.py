"""Локальная сборка диплома через установленный LaTeX toolchain.

Поддерживает сборку через latexmk и ручную цепочку LuaLaTeX/Biber, складывая
временные файлы в .aux_files и проверяя наличие внешних команд заранее.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil

from common import PROJECT_DIR, ScriptError, env_value, require_command, run_command, script_main

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


def build_with_latexmk(target: Path) -> Path:
    if not target.is_file():
        raise ScriptError(f"Указанный .tex-файл не найден: {target}")

    run_command(latexmk_command(target))

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
    run_command(lualatex_command(target))
    run_command(["biber", str(AUX_DIR / f"{target.stem}.bcf")])
    run_command(lualatex_command(target))
    run_command(lualatex_command(target))

    aux_pdf = AUX_DIR / f"{target.stem}.pdf"
    output_pdf = output_pdf_path(target)

    if not aux_pdf.is_file():
        raise ScriptError(f"PDF-файл не был создан там, где ожидалось: {aux_pdf}. " "Проверьте сообщения LaTeX выше.")

    shutil.copy2(aux_pdf, output_pdf)
    return output_pdf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Собрать LaTeX-документ через latexmk.")
    parser.add_argument(
        "--target",
        default=None,
        help="Путь к .tex-файлу. По умолчанию берется TARGET из .env.",
    )
    parser.add_argument(
        "--no-latexmk",
        action="store_true",
        help=("Не использовать latexmk. Запустить старую ручную цепочку: " "lualatex, biber, lualatex, lualatex."),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    target = target_tex_path(args.target)
    if args.no_latexmk:
        require_command("lualatex")
        require_command("biber")
        output_pdf = build_without_latexmk(target)
    else:
        require_command("latexmk")
        output_pdf = build_with_latexmk(target)

    print(f"\nГотово: {output_pdf.relative_to(PROJECT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
