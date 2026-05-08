from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

from common import PROJECT_DIR, env_value, require_command, run_command


DEFAULT_OUTPUT_DIR = PROJECT_DIR / ".pdf_diff"
DEFAULT_SAVED_DIFF_DIR = DEFAULT_OUTPUT_DIR / "saved"
FIGURES_DIR = PROJECT_DIR / "figures"
PROFILE_SERVICES = {
    "docx": "docx_pdf",
    "mermaid": "mermaid_diagrams",
    "python": "python_diagrams",
    "latex": "latex",
}
PROFILE_ORDER = ["docx", "mermaid", "python", "latex"]
PROFILE_GROUPS = {
    "all": ["docx", "mermaid", "python", "latex"],
    "docx": ["docx", "latex"],
    "latex": ["latex"],
    "mermaid": ["mermaid", "latex"],
}


def capture(command: list[str]) -> str:
    return subprocess.check_output(command, cwd=PROJECT_DIR, text=True).strip()


def docker_compose_command() -> list[str]:
    if shutil.which("docker") is not None:
        result = subprocess.run(
            ["docker", "compose", "version"],
            cwd=PROJECT_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return ["docker", "compose"]

    if shutil.which("docker-compose") is not None:
        return ["docker-compose"]

    raise RuntimeError(
        "Не найден Docker Compose. Установите Docker Desktop или docker-compose и убедитесь, "
        "что команда доступна в терминале."
    )


def target_pdf_name() -> str:
    target = env_value("TARGET")
    if target:
        return f"{Path(target).stem}.pdf"

    tex_files = sorted(PROJECT_DIR.glob("*.tex"))
    if len(tex_files) == 1:
        return f"{tex_files[0].stem}.pdf"

    raise RuntimeError(
        "Не удалось понять, какой PDF нужно сравнить. "
        "Укажите TARGET в файле .env или передайте имя PDF через --pdf."
    )


def require_clean_worktree() -> None:
    status = capture(["git", "status", "--porcelain"])
    if status:
        raise RuntimeError(
            "В проекте есть несохраненные изменения Git. Перед запуском сравнения "
            "закоммитьте, временно спрячьте через git stash или уберите локальные изменения."
        )


def safe_label(commit: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_", "."} else "_" for char in commit)


def snapshot_generated_files(snapshot_dir: Path) -> None:
    if snapshot_dir.exists():
        shutil.rmtree(snapshot_dir)

    root_pdfs_dir = snapshot_dir / "root_pdfs"
    root_pdfs_dir.mkdir(parents=True)

    for pdf_path in PROJECT_DIR.glob("*.pdf"):
        shutil.copy2(pdf_path, root_pdfs_dir / pdf_path.name)

    if FIGURES_DIR.exists():
        shutil.copytree(FIGURES_DIR, snapshot_dir / "figures")


def restore_generated_files(snapshot_dir: Path) -> None:
    if FIGURES_DIR.exists():
        shutil.rmtree(FIGURES_DIR)

    saved_figures_dir = snapshot_dir / "figures"
    if saved_figures_dir.exists():
        shutil.copytree(saved_figures_dir, FIGURES_DIR)

    for pdf_path in PROJECT_DIR.glob("*.pdf"):
        pdf_path.unlink()

    saved_root_pdfs_dir = snapshot_dir / "root_pdfs"
    if saved_root_pdfs_dir.exists():
        for pdf_path in saved_root_pdfs_dir.glob("*.pdf"):
            shutil.copy2(pdf_path, PROJECT_DIR / pdf_path.name)


def parse_profiles(value: str) -> list[str]:
    if "," not in value and value in PROFILE_GROUPS:
        return PROFILE_GROUPS[value]

    requested = [profile.strip() for profile in value.split(",") if profile.strip()]
    if not requested:
        raise argparse.ArgumentTypeError("Укажите хотя бы один Docker-профиль.")

    unknown = [profile for profile in requested if profile not in PROFILE_SERVICES]
    if unknown:
        available = ", ".join(PROFILE_ORDER)
        raise argparse.ArgumentTypeError(
            f"Неизвестный Docker-профиль: {', '.join(unknown)}. "
            f"Доступные профили: {available}."
        )

    if "latex" not in requested:
        requested.append("latex")

    return [profile for profile in PROFILE_ORDER if profile in requested]


def format_profiles(profiles: list[str]) -> str:
    return " -> ".join(profiles)


def run_profiles(profiles: list[str]) -> None:
    compose = docker_compose_command()
    print(f"Профили сборки: {format_profiles(profiles)}", flush=True)
    for profile in profiles:
        service = PROFILE_SERVICES[profile]
        run_command([*compose, "--profile", profile, "run", "--rm", service])


def build_pdf(commit: str, pdf_name: str, destination_dir: Path, profiles: list[str]) -> Path:
    run_command(["git", "checkout", "--detach", commit])

    run_profiles(profiles)

    pdf_path = PROJECT_DIR / pdf_name
    if not pdf_path.exists():
        raise RuntimeError(
            f"PDF-файл не был создан там, где ожидалось: {pdf_path}. "
            "Проверьте сообщения сборки выше."
        )

    destination = destination_dir / f"{safe_label(commit)}_{pdf_name}"
    shutil.copy2(pdf_path, destination)
    print(f"Сохранен PDF: {destination}", flush=True)
    return destination


def require_diff_pdf() -> None:
    require_command("diff-pdf")


def open_diff_pdf(left_pdf: Path, right_pdf: Path) -> int:
    require_diff_pdf()
    return subprocess.run(
        ["diff-pdf", "--view", str(left_pdf), str(right_pdf)],
        cwd=PROJECT_DIR,
    ).returncode


def save_diff_pdf(left_pdf: Path, right_pdf: Path, output_pdf: Path) -> int:
    require_diff_pdf()
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["diff-pdf", f"--output-diff={output_pdf}", str(left_pdf), str(right_pdf)],
        cwd=PROJECT_DIR,
    )
    if result.returncode == 0:
        print(f"Визуальные отличия не найдены: {output_pdf}", flush=True)
    elif result.returncode == 1:
        print(f"PDF с отличиями сохранен: {output_pdf}", flush=True)
    return result.returncode


def default_saved_diff_path(left_commit: str, right_commit: str, pdf_name: str) -> Path:
    pdf_stem = Path(pdf_name).stem
    filename = (
        f"{pdf_stem}_diff_"
        f"{safe_label(left_commit)}__{safe_label(right_commit)}.pdf"
    )
    return DEFAULT_SAVED_DIFF_DIR / filename


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Собрать PDF для двух коммитов и сравнить их через diff-pdf."
    )
    parser.add_argument("left_commit", help="Первый коммит, тег или ветка")
    parser.add_argument("right_commit", help="Второй коммит, тег или ветка")
    parser.add_argument(
        "--pdf",
        default=None,
        help="Имя PDF-файла для сравнения. По умолчанию берется TARGET из .env с расширением .pdf.",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Оставить временную папку .pdf_diff после завершения diff-pdf.",
    )
    parser.add_argument(
        "--view",
        action="store_true",
        help="Открыть визуальное сравнение в diff-pdf. Используется по умолчанию, если не указан --save.",
    )
    parser.add_argument(
        "--save",
        nargs="?",
        const=True,
        default=False,
        metavar="PATH",
        help=(
            "Сохранить PDF с визуальными отличиями вместо простого просмотра. "
            "Если PATH не указан, файл сохраняется в .pdf_diff/saved."
        ),
    )
    parser.add_argument(
        "--profiles",
        type=parse_profiles,
        default=parse_profiles("all"),
        metavar="PROFILES",
        help=(
            "Профили Docker для запуска перед сравнением. Можно указать готовую группу "
            "all, docx, mermaid, latex или список через запятую, например mermaid,python. "
            "Профиль latex добавляется автоматически, если его нет в списке."
        ),
    )
    args = parser.parse_args()
    if not args.view and not args.save:
        args.view = True
    return args


def requested_save_path(save_arg: str | bool, left_commit: str, right_commit: str, pdf_name: str) -> Path | None:
    if not save_arg:
        return None
    if save_arg is True:
        return default_saved_diff_path(left_commit, right_commit, pdf_name)
    path = Path(save_arg).expanduser()
    if not path.is_absolute():
        path = PROJECT_DIR / path
    return path.resolve()


def main() -> int:
    args = parse_args()
    original_head = capture(["git", "rev-parse", "--verify", "HEAD"])
    output_dir = DEFAULT_OUTPUT_DIR / f"{safe_label(args.left_commit)}__{safe_label(args.right_commit)}"
    snapshot_dir = DEFAULT_OUTPUT_DIR / "_restore_snapshot"
    pdf_name = args.pdf or target_pdf_name()
    save_path = requested_save_path(args.save, args.left_commit, args.right_commit, pdf_name)

    require_clean_worktree()

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    snapshot_generated_files(snapshot_dir)

    try:
        left_pdf = build_pdf(args.left_commit, pdf_name, output_dir, args.profiles)
        right_pdf = build_pdf(args.right_commit, pdf_name, output_dir, args.profiles)
        return_code = 0
        if save_path is not None:
            return_code = max(return_code, save_diff_pdf(left_pdf, right_pdf, save_path))
        if args.view:
            return_code = max(return_code, open_diff_pdf(left_pdf, right_pdf))
        return return_code
    finally:
        print(f"==> git checkout {original_head}", flush=True)
        subprocess.run(["git", "checkout", original_head], cwd=PROJECT_DIR)

        if snapshot_dir.exists():
            restore_generated_files(snapshot_dir)
            shutil.rmtree(snapshot_dir)

        if not args.keep and output_dir.exists():
            shutil.rmtree(output_dir)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as error:
        if isinstance(error, subprocess.CalledProcessError):
            print(
                f"Команда завершилась с ошибкой (код {error.returncode}): {' '.join(error.cmd)}",
                file=sys.stderr,
            )
            print("Проверьте сообщения выше: там обычно указана причина ошибки.", file=sys.stderr)
            raise SystemExit(error.returncode)

        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
