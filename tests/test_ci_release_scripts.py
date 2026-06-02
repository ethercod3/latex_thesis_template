from __future__ import annotations

import json

import pytest

from ci import download_latest_checktool_assets as download
from ci import prepare_pdf_release_env as prepare
from ci import publish_pdf_release as publish
from ci import release_check_tools as check_release
from ci import resolve_pdf_release_context as context
from common import ScriptError


def test_prepare_pdf_release_env_writes_expected_env(tmp_path, monkeypatch) -> None:
    env_path = tmp_path / ".env"
    monkeypatch.setattr(prepare, "ENV_PATH", env_path)
    monkeypatch.setattr(prepare, "host_uid", lambda: 1001)
    monkeypatch.setattr(prepare, "host_gid", lambda: 1002)

    assert prepare.main() == 0

    assert env_path.read_text(encoding="utf-8") == (
        'VAULT_PATH="/vault_code"\n'
        'VAULT_OS_PATH="./vault_diploma"\n'
        'TARGET="Куприянов_И221_диплом.tex"\n'
        "HOST_UID=1001\n"
        "HOST_GID=1002\n"
    )


def test_latest_release_tag_skips_current_tag(monkeypatch) -> None:
    releases = [{"tagName": "v0.1.3"}, {"tagName": "v0.1.2"}]
    monkeypatch.setattr(download, "capture_command", lambda command: json.dumps(releases))

    assert download.latest_release_tag("v0.1.3") == "v0.1.2"


def test_latest_release_tag_returns_none_when_only_current_tag_exists(monkeypatch) -> None:
    monkeypatch.setattr(download, "capture_command", lambda command: json.dumps([{"tagName": "v0.1.3"}]))

    assert download.latest_release_tag("v0.1.3") is None


def test_checktool_source_tag_prefers_explicit_env(monkeypatch) -> None:
    monkeypatch.setenv("CHECKTOOL_SOURCE_TAG", "v0.1.3")

    assert download.checktool_source_tag("nightly") == "v0.1.3"


def test_checktool_source_tag_falls_back_to_latest_release(monkeypatch) -> None:
    monkeypatch.delenv("CHECKTOOL_SOURCE_TAG", raising=False)
    monkeypatch.setattr(download, "latest_release_tag", lambda excluded_tag: "v0.1.2")

    assert download.checktool_source_tag("nightly") == "v0.1.2"


def test_normalize_assets_copies_aliases_to_canonical_names(tmp_path, monkeypatch) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    monkeypatch.setattr(download, "DIST_DIR", dist)
    (dist / "checktool-windows-x64.exe").write_bytes(b"exe")
    (dist / "checktool-SHA256SUMS.txt").write_text("checksum", encoding="utf-8")

    download.normalize_assets()

    assert (dist / "diploma-latex-check.exe").read_bytes() == b"exe"
    assert (dist / "SHA256SUMS.txt").read_text(encoding="utf-8") == "checksum"


def test_current_tag_requires_env(monkeypatch) -> None:
    monkeypatch.delenv("CURRENT_TAG", raising=False)

    with pytest.raises(ScriptError):
        publish.current_tag()


def test_move_nightly_tag_force_updates_only_nightly(monkeypatch) -> None:
    commands: list[list[str]] = []
    monkeypatch.setattr(publish, "run_command", lambda command: commands.append(command))

    publish.move_nightly_tag("v0.1.3")
    assert commands == []

    publish.move_nightly_tag("nightly")
    assert commands == [
        ["git", "tag", "-f", "nightly", "HEAD"],
        ["git", "push", "origin", "refs/tags/nightly", "--force"],
    ]


def test_release_tag_for_schedule_is_nightly(monkeypatch) -> None:
    monkeypatch.setattr(context, "github_event_name", lambda: "schedule")

    assert context.release_tag_for_event() == "nightly"


def test_release_tag_for_workflow_dispatch_uses_input_tag(monkeypatch) -> None:
    monkeypatch.setattr(context, "github_event_name", lambda: "workflow_dispatch")
    monkeypatch.setenv("INPUT_TAG", "v0.1.3")

    assert context.release_tag_for_event() == "v0.1.3"


def test_release_tag_for_workflow_run_uses_tag_pointing_at_head(monkeypatch) -> None:
    monkeypatch.setattr(context, "github_event_name", lambda: "workflow_run")
    monkeypatch.setattr(context, "tags_pointing_at_head", lambda: ["v0.1.2", "v0.1.3"])

    assert context.release_tag_for_event() == "v0.1.3"


def test_release_tag_for_workflow_run_accepts_plain_semver_tag(monkeypatch) -> None:
    monkeypatch.setattr(context, "github_event_name", lambda: "workflow_run")
    monkeypatch.setattr(context, "tags_pointing_at_head", lambda: ["0.2.0"])

    assert context.release_tag_for_event() == "0.2.0"


def test_checktool_source_tag_is_empty_for_nightly() -> None:
    assert context.checktool_source_tag("nightly") == ""


def test_checktool_source_tag_is_current_tag_for_version_release() -> None:
    assert context.checktool_source_tag("v0.1.3") == "v0.1.3"


def test_release_check_tools_uploads_exe_and_checksum(tmp_path, monkeypatch) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    exe = dist / "diploma-latex-check.exe"
    checksum = dist / "SHA256SUMS.txt"
    exe.write_bytes(b"exe")
    checksum.write_text("checksum", encoding="utf-8")

    commands: list[list[str]] = []

    def fake_run_checked(command: list[str]) -> tuple[int, str, str]:
        commands.append(command)
        if command == ["gh", "release", "view", "0.2.0"]:
            return 1, "", "not found"
        return 0, "ok", ""

    monkeypatch.setenv("GH_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REF_NAME", "0.2.0")
    monkeypatch.setattr(check_release, "EXE_PATH", exe)
    monkeypatch.setattr(check_release, "CHECKSUM_PATH", checksum)
    monkeypatch.setattr(check_release, "run_checked", fake_run_checked)

    check_release.main()

    assert commands == [
        ["gh", "release", "list"],
        ["gh", "release", "view", "0.2.0"],
        ["gh", "release", "create", "0.2.0", "--title", "0.2.0", "--notes", "Автоматическая сборка check tools."],
        ["gh", "release", "upload", "0.2.0", f"{exe}#checktool-windows-x64.exe", "--clobber"],
        ["gh", "release", "upload", "0.2.0", f"{checksum}#checktool-SHA256SUMS.txt", "--clobber"],
    ]
