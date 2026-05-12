from __future__ import annotations

import convert_docx_to_pdf as docx


def test_is_blank_bbox_line_detects_zero_bounding_box() -> None:
    assert docx.is_blank_bbox_line("%%BoundingBox: 0 0 0 0")


def test_is_blank_bbox_line_rejects_non_blank_bounding_box() -> None:
    assert not docx.is_blank_bbox_line("%%BoundingBox: 0 0 612 792")


def test_is_blank_bbox_line_rejects_malformed_lines() -> None:
    assert not docx.is_blank_bbox_line("%%BoundingBox:")
