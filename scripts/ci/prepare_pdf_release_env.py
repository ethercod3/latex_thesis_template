from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import PROJECT_DIR, script_main

ENV_PATH = PROJECT_DIR / ".env"
TARGET = "Куприянов_И221_диплом.tex"


def host_uid() -> int:
    getuid = getattr(os, "getuid", None)
    return getuid() if getuid else 0


def host_gid() -> int:
    getgid = getattr(os, "getgid", None)
    return getgid() if getgid else 0


def main() -> int:
    env_content = "\n".join(
        [
            'VAULT_PATH="/vault_code"',
            'VAULT_OS_PATH="./vault_diploma"',
            f'TARGET="{TARGET}"',
            f"HOST_UID={host_uid()}",
            f"HOST_GID={host_gid()}",
            "",
        ]
    )
    ENV_PATH.write_text(env_content, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
