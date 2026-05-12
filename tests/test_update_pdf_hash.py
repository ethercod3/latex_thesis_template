from __future__ import annotations

import hashlib

import update_pdf_hash as pdf_hash


def test_file_hashes_returns_expected_digests(tmp_path) -> None:
    pdf = tmp_path / "sample.pdf"
    content = b"abc"
    pdf.write_bytes(content)

    hashes = dict(pdf_hash.file_hashes(pdf))

    assert hashes["MD5"] == hashlib.md5(content).hexdigest()
    assert hashes["SHA-1"] == hashlib.sha1(content).hexdigest()
    assert hashes["SHA-256"] == hashlib.sha256(content).hexdigest()


def test_readme_block_contains_markers_and_hash_lines() -> None:
    block = pdf_hash.readme_block([("SHA-256", "abc123")])

    assert pdf_hash.START_MARKER in block
    assert "SHA-256: `abc123`<br>" in block
    assert pdf_hash.END_MARKER in block


def test_update_readme_replaces_existing_block(tmp_path, monkeypatch) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        f"# Title\n\n{pdf_hash.START_MARKER}\nold\n{pdf_hash.END_MARKER}\n\nBody\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(pdf_hash, "README_PATH", readme)

    changed = pdf_hash.update_readme([("SHA-256", "new")])

    content = readme.read_text(encoding="utf-8")
    assert changed is True
    assert "old" not in content
    assert "SHA-256: `new`<br>" in content
    assert "Body" in content


def test_update_readme_inserts_block_after_title(tmp_path, monkeypatch) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n\nBody\n", encoding="utf-8")
    monkeypatch.setattr(pdf_hash, "README_PATH", readme)

    changed = pdf_hash.update_readme([("MD5", "digest")])

    assert changed is True
    assert readme.read_text(encoding="utf-8").startswith("# Title\n\n<!-- DIPLOMA_HASHES_START -->")
