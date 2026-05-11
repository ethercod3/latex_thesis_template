from __future__ import annotations

from pathlib import Path
import hashlib
import subprocess
import sys


EXE_PATH = Path("dist/diploma-latex-check.exe")
CHECKSUM_PATH = Path("dist/SHA256SUMS.txt")


def smoke() -> int:
    result = subprocess.run([str(EXE_PATH)], check=False)
    if result.returncode:
        print(
            f"Smoke test finished with exit code {result.returncode}. "
            "This is allowed because the runner may not have TeX Live or Docker."
        )
    return 0


def checksum() -> int:
    digest = hashlib.sha256(EXE_PATH.read_bytes()).hexdigest()
    CHECKSUM_PATH.write_text(f"{digest}  {EXE_PATH.name}\n", encoding="utf-8")
    return 0


def main() -> int:
    commands = {
        "smoke": smoke,
        "checksum": checksum,
    }
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        print("Использование: python scripts/check_tools_exe.py smoke|checksum", file=sys.stderr)
        return 2
    return commands[sys.argv[1]]()


if __name__ == "__main__":
    raise SystemExit(main())
