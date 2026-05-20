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


def test_readme_body_contains_hash_lines() -> None:
    body = pdf_hash.readme_body([("SHA-256", "abc123")])

    assert body == "## Контрольные суммы PDF\n\nSHA-256: `abc123`<br>\n"


def test_cog_readme_block_uses_pdf_from_environment(tmp_path, monkeypatch) -> None:
    pdf = tmp_path / "sample.pdf"
    pdf.write_bytes(b"abc")

    monkeypatch.setenv(pdf_hash.PDF_ENV_VAR, str(pdf))

    body = pdf_hash.cog_readme_block()

    assert "MD5: `900150983cd24fb0d6963f7d28e17f72`<br>" in body
