from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

from dotenv import dotenv_values


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_DIR / ".pdf_diff"
FIGURES_DIR = PROJECT_DIR / "figures"
PROFILE_SERVICES = {
    "docx": "docx_pdf",
    "mermaid": "mermaid_diagrams",
    "python": "python_diagrams",
    "latex": "latex",
}
PROFILE_GROUPS = {
    "all": ["docx", "mermaid", "python", "latex"],
    "docx": ["docx", "latex"],
    "latex": ["latex"],
    "mermaid": ["mermaid", "latex"],
}


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

    raise RuntimeError("Docker Compose was not found in PATH")


def env_value(name: str) -> str | None:
    env_path = PROJECT_DIR / ".env"
    if not env_path.exists():
        return None

    value = dotenv_values(env_path).get(name)
    return value if value else None


def target_pdf_name() -> str:
    target = env_value("TARGET")
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


def run_profiles(profile_group: str) -> None:
    compose = docker_compose_command()
    for profile in PROFILE_GROUPS[profile_group]:
        service = PROFILE_SERVICES[profile]
        run([*compose, "--profile", profile, "run", "--rm", "--build", service])


def build_pdf(commit: str, pdf_name: str, destination_dir: Path, profile_group: str) -> Path:
    run(["git", "checkout", "--detach", commit])

    run_profiles(profile_group)

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
    parser.add_argument(
        "--profiles",
        choices=sorted(PROFILE_GROUPS),
        default="all",
        help=(
            "Docker profile group to run before comparing. "
            "all: docx, mermaid, python, latex; docx: docx, latex; "
            "mermaid: mermaid, latex; latex: latex only."
        ),
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
    snapshot_generated_files(snapshot_dir)

    try:
        left_pdf = build_pdf(args.left_commit, pdf_name, output_dir, args.profiles)
        right_pdf = build_pdf(args.right_commit, pdf_name, output_dir, args.profiles)
        return open_diff_pdf(left_pdf, right_pdf)
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
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
