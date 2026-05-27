"""Снимок и восстановление артефактов PDF diff."""

from __future__ import annotations

from pathlib import Path
import shutil

from .config import FIGURES_DIR
from common import PROJECT_DIR


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
