"""Запуск сравнения PDF между двумя git-коммитами."""

from __future__ import annotations

from pathlib import Path
import shutil

from common import (
    PROJECT_DIR,
    ScriptError,
    capture_command,
    docker_compose_command,
    require_command,
    run_command,
)

from .config import DiffPdfConfig, PROFILE_SERVICES, format_profiles, safe_label
from .state import restore_generated_files, snapshot_generated_files


class PdfDiffRunner:
    def __init__(self, config: DiffPdfConfig) -> None:
        self.config = config
        self.snapshot_dir = PROJECT_DIR / ".pdf_diff" / "_restore_snapshot"
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
