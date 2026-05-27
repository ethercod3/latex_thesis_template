"""Конфигурация и парсинг параметров для PDF diff."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from common import PROJECT_DIR, ScriptError, env_value

DEFAULT_OUTPUT_DIR = PROJECT_DIR / ".pdf_diff"
DEFAULT_SAVED_DIFF_DIR = DEFAULT_OUTPUT_DIR / "saved"
FIGURES_DIR = PROJECT_DIR / "figures"
PROFILE_SERVICES = {
    "docx": "docx_pdf",
    "mermaid": "mermaid_diagrams",
    "python": "python_diagrams",
    "latex": "latex",
}
PROFILE_ORDER = ["docx", "mermaid", "python", "latex"]
PROFILE_GROUPS = {
    "all": ["docx", "mermaid", "python", "latex"],
    "docx": ["docx", "latex"],
    "latex": ["latex"],
    "mermaid": ["mermaid", "latex"],
}


@dataclass(frozen=True)
class DiffPdfConfig:
    left_commit: str
    right_commit: str
    pdf_name: str
    profiles: list[str]
    keep: bool
    view: bool
    save_path: Path | None

    @property
    def output_dir(self) -> Path:
        return DEFAULT_OUTPUT_DIR / f"{safe_label(self.left_commit)}__{safe_label(self.right_commit)}"


def target_pdf_name() -> str:
    target = env_value("TARGET")
    if target:
        return f"{Path(target).stem}.pdf"

    tex_files = sorted(PROJECT_DIR.glob("*.tex"))
    if len(tex_files) == 1:
        return f"{tex_files[0].stem}.pdf"

    raise ScriptError(
        "Не удалось понять, какой PDF нужно сравнить. Укажите TARGET в файле .env " "или передайте имя PDF через --pdf."
    )


def safe_label(commit: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_", "."} else "_" for char in commit)


def parse_profiles(value: str) -> list[str]:
    if "," not in value and value in PROFILE_GROUPS:
        return PROFILE_GROUPS[value]

    requested = [profile.strip() for profile in value.split(",") if profile.strip()]
    if not requested:
        raise ValueError("Укажите хотя бы один Docker-профиль.")

    unknown = [profile for profile in requested if profile not in PROFILE_SERVICES]
    if unknown:
        available = ", ".join(PROFILE_ORDER)
        raise ValueError(f"Неизвестный Docker-профиль: {', '.join(unknown)}. Доступные профили: {available}.")

    if "latex" not in requested:
        requested.append("latex")

    return [profile for profile in PROFILE_ORDER if profile in requested]


def format_profiles(profiles: list[str]) -> str:
    return " -> ".join(profiles)


def default_saved_diff_path(left_commit: str, right_commit: str, pdf_name: str) -> Path:
    pdf_stem = Path(pdf_name).stem
    filename = f"{pdf_stem}_diff_{safe_label(left_commit)}__{safe_label(right_commit)}.pdf"
    return DEFAULT_SAVED_DIFF_DIR / filename


def requested_save_path(save_arg: str | bool, left_commit: str, right_commit: str, pdf_name: str) -> Path | None:
    if not save_arg:
        return None
    if save_arg is True:
        return default_saved_diff_path(left_commit, right_commit, pdf_name)
    path = Path(save_arg).expanduser()
    if not path.is_absolute():
        path = PROJECT_DIR / path
    return path.resolve()
