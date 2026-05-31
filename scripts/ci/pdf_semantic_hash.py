"""QPDF-normalized PDF hash for archive deduplication."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


def run_qpdf_normalize(source: Path, target: Path) -> None:
    command = [
        "qpdf",
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
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
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

    print(semantic_hash(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
