"""Вычисление GitHub Actions контекста для PDF-релиза.

Решает, какой tag и заголовок использовать для nightly или tag-сборки, и
экспортирует значения через GITHUB_ENV для последующих шагов workflow.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

import typer

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
        raise typer.BadParameter("INPUT_TAG не задан для workflow_dispatch.")
    return tag


def run_checked(command: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def tags_pointing_at_head() -> list[str]:
    run_checked(["git", "fetch", "--tags", "--force"])
    code, stdout, stderr = run_checked(["git", "tag", "--points-at", "HEAD", "--list", "v*", "[0-9]*"])
    if code != 0:
        details = stderr.strip() or stdout.strip() or "вывода нет"
        raise typer.Exit(code=code)
    return sorted(line.strip() for line in stdout.splitlines() if line.strip())


def workflow_run_tag() -> str:
    tags = tags_pointing_at_head()
    if not tags:
        raise typer.BadParameter("Не найден релизный тег v* или [0-9]*, указывающий на HEAD workflow_run checkout.")
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
        raise typer.BadParameter("Не удалось определить release tag.")
    return tag


def checktool_source_tag(release_tag: str) -> str:
    if release_tag == NIGHTLY_TAG:
        return ""
    return release_tag


def main() -> None:
    release_tag = release_tag_for_event()
    write_github_env("CURRENT_TAG", release_tag)
    write_github_env("CHECKTOOL_SOURCE_TAG", checktool_source_tag(release_tag))
    print(f"Release tag: {release_tag}")


if __name__ == "__main__":
    typer.run(main)
