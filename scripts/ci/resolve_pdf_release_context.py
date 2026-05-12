from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import ScriptError, capture_command, run_command, script_main

NIGHTLY_TAG = "nightly"


def github_event_name() -> str:
    return os.environ.get("GITHUB_EVENT_NAME", "")


def write_github_env(name: str, value: str) -> None:
    github_env = os.environ.get("GITHUB_ENV")
    if not github_env:
        print(f"{name}={value}")
        return

    with Path(github_env).open("a", encoding="utf-8", newline="\n") as file:
        file.write(f"{name}={value}\n")


def workflow_dispatch_tag() -> str:
    tag = os.environ.get("INPUT_TAG")
    if not tag:
        raise ScriptError("INPUT_TAG не задан для workflow_dispatch.")
    return tag


def tags_pointing_at_head() -> list[str]:
    run_command(["git", "fetch", "--tags", "--force"])
    output = capture_command(["git", "tag", "--points-at", "HEAD", "--list", "v*"])
    return sorted(line.strip() for line in output.splitlines() if line.strip())


def workflow_run_tag() -> str:
    tags = tags_pointing_at_head()
    if not tags:
        raise ScriptError("Не найден тег v*, указывающий на HEAD workflow_run checkout.")
    return tags[-1]


def release_tag_for_event() -> str:
    event_name = github_event_name()
    if event_name == "schedule":
        return NIGHTLY_TAG
    if event_name == "workflow_dispatch":
        return workflow_dispatch_tag()
    if event_name == "workflow_run":
        return workflow_run_tag()
    tag = os.environ.get("GITHUB_REF_NAME")
    if not tag:
        raise ScriptError("Не удалось определить release tag.")
    return tag


def checktool_source_tag(release_tag: str) -> str:
    if release_tag == NIGHTLY_TAG:
        return ""
    return release_tag


def main() -> int:
    release_tag = release_tag_for_event()
    write_github_env("CURRENT_TAG", release_tag)
    write_github_env("CHECKTOOL_SOURCE_TAG", checktool_source_tag(release_tag))
    print(f"Release tag: {release_tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
