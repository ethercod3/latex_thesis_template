from __future__ import annotations

import json

import pytest

from ci import download_latest_checktool_assets as download
from ci import prepare_pdf_release_env as prepare
from ci import publish_pdf_release as publish
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
