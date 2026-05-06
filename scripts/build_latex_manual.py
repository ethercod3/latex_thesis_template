from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

from dotenv import dotenv_values


PROJECT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_DIR / ".env"
AUX_DIR = PROJECT_DIR / ".aux_files"


def env_value(name: str) -> str | None:
    if not ENV_PATH.exists():
        return None

    value = dotenv_values(ENV_PATH).get(name)
    return value if value else None


def target_tex_path(target_arg: str | None) -> Path:
    if target_arg:
        return (PROJECT_DIR / target_arg).resolve()

    target = env_value("TARGET")
    if target:
        return (PROJECT_DIR / target).resolve()

    tex_files = sorted(PROJECT_DIR.glob("*.tex"))
    if len(tex_files) == 1:
        return tex_files[0].resolve()

    raise RuntimeError(
        "Не удалось понять, какой .tex-файл нужно собрать. "
        "Укажите TARGET в файле .env или передайте путь через --target."
    )


def require_command(command: str) -> None:
    if shutil.which(command) is None:
        raise RuntimeError(
            f"Не найдена команда '{command}'. Установите нужную программу и убедитесь, "
            "что она доступна в терминале."
        )


def run_command(command: list[str]) -> None:
    print(f"\n==> {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=PROJECT_DIR, check=True)


def lualatex_command(target: Path) -> list[str]:
    return [
        "lualatex",
        "-synctex=1",
        "-interaction=nonstopmode",
        '-output-directory=.aux_files',
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
        raise RuntimeError(f"Указанный .tex-файл не найден: {target}")

    run_command(latexmk_command(target))

    output_pdf = output_pdf_path(target)
    if not output_pdf.is_file():
        raise RuntimeError(
            f"PDF-файл не был создан там, где ожидалось: {output_pdf}. "
            "Проверьте сообщения latexmk выше."
        )

    return output_pdf


def build_without_latexmk(target: Path) -> Path:
    if not target.is_file():
        raise RuntimeError(f"Указанный .tex-файл не найден: {target}")

    AUX_DIR.mkdir(exist_ok=True)
    run_command(lualatex_command(target))
    run_command(["biber", str(AUX_DIR / f"{target.stem}.bcf")])
    run_command(lualatex_command(target))
    run_command(lualatex_command(target))

    aux_pdf = AUX_DIR / f"{target.stem}.pdf"
    output_pdf = output_pdf_path(target)

    if not aux_pdf.is_file():
        raise RuntimeError(
            f"PDF-файл не был создан там, где ожидалось: {aux_pdf}. "
            "Проверьте сообщения LaTeX выше."
        )

    shutil.copy2(aux_pdf, output_pdf)
    return output_pdf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Собрать LaTeX-документ через latexmk."
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Путь к .tex-файлу. По умолчанию берется TARGET из .env.",
    )
    parser.add_argument(
        "--no-latexmk",
        action="store_true",
        help=(
            "Не использовать latexmk. Запустить старую ручную цепочку: "
            "lualatex, biber, lualatex, lualatex."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        target = target_tex_path(args.target)
        if args.no_latexmk:
            require_command("lualatex")
            require_command("biber")
            output_pdf = build_without_latexmk(target)
        else:
            require_command("latexmk")
            output_pdf = build_with_latexmk(target)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(
            f"Команда завершилась с ошибкой (код {error.returncode}): {' '.join(error.cmd)}",
            file=sys.stderr,
        )
        print("Проверьте сообщения выше: там обычно указана причина ошибки сборки.", file=sys.stderr)
        return error.returncode

    print(f"\nГотово: {output_pdf.relative_to(PROJECT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
