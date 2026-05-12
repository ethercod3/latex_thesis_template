from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import shutil

from common import (
    PROJECT_DIR,
    ScriptError,
    capture_command,
    docker_compose_command,
    env_value,
    require_command,
    run_command,
    script_main,
)

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


@dataclass(frozen=True)
class DiffPdfConfig:
    left_commit: str
    right_commit: str
    pdf_name: str
    profiles: list[str]
    keep: bool
    view: bool
    save_path: Path | None

    @property
    def output_dir(self) -> Path:
        return DEFAULT_OUTPUT_DIR / f"{safe_label(self.left_commit)}__{safe_label(self.right_commit)}"


def target_pdf_name() -> str:
    target = env_value("TARGET")
    if target:
        return f"{Path(target).stem}.pdf"

    tex_files = sorted(PROJECT_DIR.glob("*.tex"))
    if len(tex_files) == 1:
        return f"{tex_files[0].stem}.pdf"

    raise ScriptError(
        "Не удалось понять, какой PDF нужно сравнить. Укажите TARGET в файле .env " "или передайте имя PDF через --pdf."
    )


def safe_label(commit: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_", "."} else "_" for char in commit)


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
            f"Неизвестный Docker-профиль: {', '.join(unknown)}. Доступные профили: {available}."
        )

    if "latex" not in requested:
        requested.append("latex")

    return [profile for profile in PROFILE_ORDER if profile in requested]


def format_profiles(profiles: list[str]) -> str:
    return " -> ".join(profiles)


def default_saved_diff_path(left_commit: str, right_commit: str, pdf_name: str) -> Path:
    pdf_stem = Path(pdf_name).stem
    filename = f"{pdf_stem}_diff_{safe_label(left_commit)}__{safe_label(right_commit)}.pdf"
    return DEFAULT_SAVED_DIFF_DIR / filename


def requested_save_path(save_arg: str | bool, left_commit: str, right_commit: str, pdf_name: str) -> Path | None:
    if not save_arg:
        return None
    if save_arg is True:
        return default_saved_diff_path(left_commit, right_commit, pdf_name)
    path = Path(save_arg).expanduser()
    if not path.is_absolute():
        path = PROJECT_DIR / path
    return path.resolve()


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


class PdfDiffRunner:
    def __init__(self, config: DiffPdfConfig) -> None:
        self.config = config
        self.snapshot_dir = DEFAULT_OUTPUT_DIR / "_restore_snapshot"
        self.original_head = capture_command(["git", "rev-parse", "--verify", "HEAD"])

    def run(self) -> int:
        self.require_clean_worktree()
        self.prepare_output()
        snapshot_generated_files(self.snapshot_dir)

        try:
            left_pdf = self.build_pdf(self.config.left_commit)
            right_pdf = self.build_pdf(self.config.right_commit)
            return self.compare(left_pdf, right_pdf)
        finally:
            self.restore_project_state()

    def require_clean_worktree(self) -> None:
        if capture_command(["git", "status", "--porcelain"]):
            raise ScriptError(
                "В проекте есть несохраненные изменения Git. Перед запуском сравнения "
                "закоммитьте, временно спрячьте через git stash или уберите локальные изменения."
            )

    def prepare_output(self) -> None:
        if self.config.output_dir.exists():
            shutil.rmtree(self.config.output_dir)
        self.config.output_dir.mkdir(parents=True)

    def build_pdf(self, commit: str) -> Path:
        run_command(["git", "checkout", "--detach", commit])
        self.run_profiles()

        pdf_path = PROJECT_DIR / self.config.pdf_name
        if not pdf_path.exists():
            raise ScriptError(
                f"PDF-файл не был создан там, где ожидалось: {pdf_path}. Проверьте сообщения сборки выше."
            )

        destination = self.config.output_dir / f"{safe_label(commit)}_{self.config.pdf_name}"
        shutil.copy2(pdf_path, destination)
        print(f"Сохранен PDF: {destination}", flush=True)
        return destination

    def run_profiles(self) -> None:
        compose = docker_compose_command()
        print(f"Профили сборки: {format_profiles(self.config.profiles)}", flush=True)
        for profile in self.config.profiles:
            service = PROFILE_SERVICES[profile]
            run_command([*compose, "--profile", profile, "run", "--build", "--rm", service])

    def compare(self, left_pdf: Path, right_pdf: Path) -> int:
        return_code = 0
        if self.config.save_path is not None:
            return_code = max(return_code, self.save_diff_pdf(left_pdf, right_pdf))
        if self.config.view:
            return_code = max(return_code, self.open_diff_pdf(left_pdf, right_pdf))
        return return_code

    def open_diff_pdf(self, left_pdf: Path, right_pdf: Path) -> int:
        require_command("diff-pdf")
        return run_command(["diff-pdf", "--view", str(left_pdf), str(right_pdf)], check=False).returncode

    def save_diff_pdf(self, left_pdf: Path, right_pdf: Path) -> int:
        require_command("diff-pdf")
        assert self.config.save_path is not None
        self.config.save_path.parent.mkdir(parents=True, exist_ok=True)
        result = run_command(
            ["diff-pdf", f"--output-diff={self.config.save_path}", str(left_pdf), str(right_pdf)],
            check=False,
        )
        if result.returncode == 0:
            print(f"Визуальные отличия не найдены: {self.config.save_path}", flush=True)
        elif result.returncode == 1:
            print(f"PDF с отличиями сохранен: {self.config.save_path}", flush=True)
        return result.returncode

    def restore_project_state(self) -> None:
        run_command(["git", "checkout", self.original_head], check=False)

        if self.snapshot_dir.exists():
            restore_generated_files(self.snapshot_dir)
            shutil.rmtree(self.snapshot_dir)

        if not self.config.keep and self.config.output_dir.exists():
            shutil.rmtree(self.config.output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Собрать PDF для двух коммитов и сравнить их через diff-pdf.")
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


def config_from_args(args: argparse.Namespace) -> DiffPdfConfig:
    pdf_name = args.pdf or target_pdf_name()
    return DiffPdfConfig(
        left_commit=args.left_commit,
        right_commit=args.right_commit,
        pdf_name=pdf_name,
        profiles=args.profiles,
        keep=args.keep,
        view=args.view,
        save_path=requested_save_path(args.save, args.left_commit, args.right_commit, pdf_name),
    )


def main() -> int:
    return PdfDiffRunner(config_from_args(parse_args())).run()


if __name__ == "__main__":
    raise SystemExit(script_main(main))
