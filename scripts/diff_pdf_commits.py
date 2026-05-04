from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_DIR / ".pdf_diff"
FIGURES_DIR = PROJECT_DIR / "figures"
BUILD_SCRIPT_CANDIDATES = [
    PROJECT_DIR / "scripts" / "build_app.py",
    PROJECT_DIR / "scripts" / "build_all.py",
]


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"==> {' '.join(command)}", flush=True)
    return subprocess.run(
        command,
        cwd=PROJECT_DIR,
        check=check,
        text=True,
        stdout=None,
        stderr=None,
    )


def capture(command: list[str]) -> str:
    return subprocess.check_output(command, cwd=PROJECT_DIR, text=True).strip()


def parse_env_value(name: str) -> str | None:
    env_path = PROJECT_DIR / ".env"
    if not env_path.exists():
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        if key.strip() != name:
            continue

        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        return value

    return None


def target_pdf_name() -> str:
    target = parse_env_value("TARGET")
    if target:
        return f"{Path(target).stem}.pdf"

    tex_files = sorted(PROJECT_DIR.glob("*.tex"))
    if len(tex_files) == 1:
        return f"{tex_files[0].stem}.pdf"

    raise RuntimeError("Cannot determine target PDF. Set TARGET in .env or pass --pdf.")


def require_clean_worktree() -> None:
    status = capture(["git", "status", "--porcelain"])
    if status:
        raise RuntimeError(
            "Git worktree is not clean. Commit, stash, or remove local changes before "
            "running this script."
        )


def safe_label(commit: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_", "."} else "_" for char in commit)


def build_script_path() -> Path:
    for candidate in BUILD_SCRIPT_CANDIDATES:
        if candidate.exists():
            return candidate

    names = ", ".join(str(path.relative_to(PROJECT_DIR)) for path in BUILD_SCRIPT_CANDIDATES)
    raise RuntimeError(f"Build script was not found. Expected one of: {names}")


def prepare_build_script() -> Path:
    source = build_script_path()
    destination = PROJECT_DIR / "scripts" / f".diff_pdf_{source.name}"
    shutil.copy2(source, destination)
    return destination


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


def build_pdf(commit: str, pdf_name: str, destination_dir: Path, build_script: Path) -> Path:
    run(["git", "checkout", "--detach", commit])

    run([sys.executable, str(build_script)])

    pdf_path = PROJECT_DIR / pdf_name
    if not pdf_path.exists():
        raise RuntimeError(f"Expected PDF was not created: {pdf_path}")

    destination = destination_dir / f"{safe_label(commit)}_{pdf_name}"
    shutil.copy2(pdf_path, destination)
    print(f"Saved {destination}", flush=True)
    return destination


def open_diff_pdf(left_pdf: Path, right_pdf: Path) -> int:
    if shutil.which("diff-pdf") is None:
        raise RuntimeError("diff-pdf was not found in PATH")

    return subprocess.run(
        ["diff-pdf", "--view", str(left_pdf), str(right_pdf)],
        cwd=PROJECT_DIR,
    ).returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build PDFs for two commits and open their visual diff in diff-pdf."
    )
    parser.add_argument("left_commit", help="First commit hash/ref")
    parser.add_argument("right_commit", help="Second commit hash/ref")
    parser.add_argument(
        "--pdf",
        default=None,
        help="PDF filename to compare. Defaults to TARGET from .env with .pdf extension.",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep the temporary .pdf_diff directory after diff-pdf exits.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    original_head = capture(["git", "rev-parse", "--verify", "HEAD"])
    output_dir = DEFAULT_OUTPUT_DIR / f"{safe_label(args.left_commit)}__{safe_label(args.right_commit)}"
    snapshot_dir = DEFAULT_OUTPUT_DIR / "_restore_snapshot"
    pdf_name = args.pdf or target_pdf_name()

    require_clean_worktree()

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    build_script = prepare_build_script()
    snapshot_generated_files(snapshot_dir)

    try:
        left_pdf = build_pdf(args.left_commit, pdf_name, output_dir, build_script)
        right_pdf = build_pdf(args.right_commit, pdf_name, output_dir, build_script)
        return open_diff_pdf(left_pdf, right_pdf)
    finally:
        print(f"==> git checkout {original_head}", flush=True)
        subprocess.run(["git", "checkout", original_head], cwd=PROJECT_DIR)

        if build_script.exists():
            build_script.unlink()

        if snapshot_dir.exists():
            restore_generated_files(snapshot_dir)
            shutil.rmtree(snapshot_dir)

        if not args.keep and output_dir.exists():
            shutil.rmtree(output_dir)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
