"""QPDF-normalized PDF hash for archive deduplication."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def qpdf_command() -> str:
    configured = os.environ.get("QPDF")
    if configured:
        return configured

    found = shutil.which("qpdf")
    if found:
        return found

    chocolatey_qpdf = Path(r"C:\ProgramData\chocolatey\bin\qpdf.exe")
    if chocolatey_qpdf.is_file():
        return str(chocolatey_qpdf)

    return "qpdf"


def run_qpdf_normalize(source: Path, target: Path) -> None:
    qpdf = qpdf_command()
    command = [
        qpdf,
        "--deterministic-id",
        "--object-streams=disable",
        "--stream-data=uncompress",
        "--normalize-content=y",
        "--empty",
        "--pages",
        str(source),
        "1-z",
        "--",
        str(target),
    ]
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "qpdf is required to compute semantic PDF hashes. "
            "Install qpdf, add it to PATH, or set QPDF to the qpdf executable path."
        ) from exc
    if result.returncode not in (0, 3):
        details = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"qpdf failed for {source}: {details}")


def semantic_hash(path: Path) -> str:
    with tempfile.TemporaryDirectory(prefix="pdf-semantic-hash-") as tmp_dir:
        normalized = Path(tmp_dir) / "normalized.pdf"
        run_qpdf_normalize(path, normalized)
        return hashlib.sha256(normalized.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: pdf_semantic_hash.py <pdf>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"PDF file not found: {path}", file=sys.stderr)
        return 1

    try:
        print(semantic_hash(path))
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
