from __future__ import annotations

from pathlib import Path

import compile_mermaid


def test_process_file_crops_generated_pdf(monkeypatch, tmp_path: Path) -> None:
    src = tmp_path / "diagram.mmd"
    out_dir = tmp_path / "figures"
    src.write_text("flowchart TD\nA-->B\n", encoding="utf-8")
    out_dir.mkdir()

    monkeypatch.setattr(compile_mermaid, "DST", out_dir)

    calls: list[tuple[str, ...]] = []

    def fake_run(command: list[str], **kwargs: object) -> object:
        calls.append(tuple(command))
        if command[0] == "mmdc":
            Path(command[4]).write_text("generated", encoding="utf-8")
        if command[0] == "pdfcrop":
            Path(command[2]).write_text("cropped", encoding="utf-8")
        return object()

    monkeypatch.setattr(compile_mermaid.subprocess, "run", fake_run)

    result = compile_mermaid.process_file(src, ["mmdc"], ["pdfcrop"])

    assert result == "[OK] diagram.mmd -> diagram.pdf"
    assert (out_dir / "diagram.pdf").read_text(encoding="utf-8") == "cropped"
    assert calls == [
        ("mmdc", "-i", str(src), "-o", str(out_dir / "diagram.pdf"), "-f"),
        ("pdfcrop", str(out_dir / "diagram.pdf"), str(out_dir / "diagram.pdfcrop-tmp.pdf")),
    ]


def test_process_file_can_skip_crop(monkeypatch, tmp_path: Path) -> None:
    src = tmp_path / "diagram.mmd"
    out_dir = tmp_path / "figures"
    src.write_text("flowchart TD\nA-->B\n", encoding="utf-8")
    out_dir.mkdir()

    monkeypatch.setattr(compile_mermaid, "DST", out_dir)

    calls: list[tuple[str, ...]] = []

    def fake_run(command: list[str], **kwargs: object) -> object:
        calls.append(tuple(command))
        Path(command[4]).write_text("generated", encoding="utf-8")
        return object()

    monkeypatch.setattr(compile_mermaid.subprocess, "run", fake_run)

    result = compile_mermaid.process_file(src, ["mmdc"], None)

    assert result == "[OK] diagram.mmd -> diagram.pdf"
    assert (out_dir / "diagram.pdf").read_text(encoding="utf-8") == "generated"
    assert calls == [("mmdc", "-i", str(src), "-o", str(out_dir / "diagram.pdf"), "-f")]


def test_main_returns_error_when_any_diagram_fails(monkeypatch, tmp_path: Path) -> None:
    src_dir = tmp_path / "mermaid"
    out_dir = tmp_path / "figures"
    src_dir.mkdir()
    src = src_dir / "broken.mmd"
    src.write_text("flowchart TD\nA-->B\n", encoding="utf-8")

    monkeypatch.setattr(compile_mermaid, "SRC", src_dir)
    monkeypatch.setattr(compile_mermaid, "DST", out_dir)
    monkeypatch.setattr(compile_mermaid, "find_mmdc", lambda: ["mmdc"])
    monkeypatch.setattr(compile_mermaid, "find_pdfcrop", lambda: ["pdfcrop"])
    monkeypatch.setattr(compile_mermaid, "parse_args", lambda: type("Args", (), {"no_crop": False})())
    monkeypatch.setattr(
        compile_mermaid,
        "process_file",
        lambda f, mmdc, pdfcrop: f"[ОШИБКА] Не удалось собрать диаграмму {f.name}",
    )

    assert compile_mermaid.main() == 1
