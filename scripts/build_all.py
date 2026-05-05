from pathlib import Path
import shutil
import subprocess
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROFILES = [
    ("docx", "docx_pdf"),
    ("mermaid", "mermaid_diagrams"),
    ("python", "python_diagrams"),
    ("latex", "latex"),
]


def run_profile(profile: str, service: str) -> int:
    print(f"\n==> {profile}", flush=True)

    result = subprocess.run(
        [
            "docker",
            "compose",
            "--profile",
            profile,
            "run",
            "--rm",
            service,
        ],
        cwd=PROJECT_DIR,
    )

    return result.returncode


def main() -> int:
    if shutil.which("docker") is None:
        print("Docker was not found in PATH", file=sys.stderr)
        return 1

    for profile, service in PROFILES:
        exit_code = run_profile(profile, service)
        if exit_code != 0:
            return exit_code

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
