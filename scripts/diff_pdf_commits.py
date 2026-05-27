"""Сравнение PDF, собранных из двух git-коммитов.

Wrapper над пакетом `pdfdiff`.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from pdfdiff.cli import main, run
from pdfdiff.config import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SAVED_DIFF_DIR,
    FIGURES_DIR,
    PROFILE_GROUPS,
    PROFILE_ORDER,
    PROFILE_SERVICES,
    DiffPdfConfig,
    default_saved_diff_path,
    format_profiles,
    parse_profiles,
    requested_save_path,
    safe_label,
    target_pdf_name,
)
from pdfdiff.runner import PdfDiffRunner

__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_SAVED_DIFF_DIR",
    "FIGURES_DIR",
    "PROFILE_GROUPS",
    "PROFILE_ORDER",
    "PROFILE_SERVICES",
    "DiffPdfConfig",
    "PdfDiffRunner",
    "default_saved_diff_path",
    "format_profiles",
    "main",
    "parse_profiles",
    "requested_save_path",
    "run",
    "safe_label",
    "target_pdf_name",
]


if __name__ == "__main__":
    run()
