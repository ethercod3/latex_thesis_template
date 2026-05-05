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

    raise RuntimeError("Cannot determine target .tex file. Set TARGET in .env or pass --target.")


def require_command(command: str) -> None:
    if shutil.which(command) is None:
        raise RuntimeError(f"{command} was not found in PATH")


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


def build(target: Path) -> Path:
    if not target.is_file():
        raise RuntimeError(f"Target .tex file was not found: {target}")

    AUX_DIR.mkdir(exist_ok=True)

    run_command(lualatex_command(target))
    run_command(["biber", str(AUX_DIR / f"{target.stem}.bcf")])
    run_command(lualatex_command(target))
    run_command(lualatex_command(target))

    aux_pdf = AUX_DIR / f"{target.stem}.pdf"
    output_pdf = PROJECT_DIR / f"{target.stem}.pdf"

    if not aux_pdf.is_file():
        raise RuntimeError(f"Expected PDF was not produced: {aux_pdf}")

    shutil.copy2(aux_pdf, output_pdf)
    return output_pdf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the LaTeX document manually with lualatex and biber."
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Target .tex file. Defaults to TARGET from .env.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        require_command("lualatex")
        require_command("biber")
        target = target_tex_path(args.target)
        output_pdf = build(target)
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        return 1

    print(f"\nBuilt {output_pdf.relative_to(PROJECT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
