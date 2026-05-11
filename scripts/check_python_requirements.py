from __future__ import annotations

from importlib import metadata
from pathlib import Path
import re
import sys


def requirement_name(line: str) -> str:
    package = line.strip()
    if not package or package.startswith("#"):
        return ""
    return re.split(r"[<>=!~]", package, maxsplit=1)[0].strip()


def missing_requirements(requirements_path: Path) -> list[str]:
    missing: list[str] = []
    for line in requirements_path.read_text(encoding="utf-8").splitlines():
        package = requirement_name(line)
        if not package:
            continue
        try:
            metadata.version(package)
        except metadata.PackageNotFoundError:
            missing.append(package)
    return missing


def main() -> int:
    if len(sys.argv) != 2:
        print("Использование: python scripts/check_python_requirements.py requirements.txt", file=sys.stderr)
        return 2

    requirements_path = Path(sys.argv[1])
    print("\n".join(missing_requirements(requirements_path)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
