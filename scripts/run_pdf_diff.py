"""Run diff-pdf-commits using project-local diff_config.toml."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

from common import PROJECT_DIR, ScriptError, env_value, script_main

CONFIG_PATH = PROJECT_DIR / "diff_config.toml"


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.is_file():
        raise ScriptError(f"Не найден конфиг сравнения PDF: {CONFIG_PATH}")
    with CONFIG_PATH.open("rb") as config_file:
        data = tomllib.load(config_file)
    section = data.get("diff_pdf")
    if not isinstance(section, dict):
        raise ScriptError("В diff_config.toml должна быть секция [diff_pdf].")
    return section


def string_value(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ScriptError(f"В diff_config.toml параметр {name} должен быть непустой строкой.")
    return value


def target_from_args(extra_args: list[str]) -> str:
    target = env_value("TARGET")
    for index, arg in enumerate(extra_args):
        if arg == "--env" and index + 1 < len(extra_args):
            key, separator, value = extra_args[index + 1].partition("=")
            if separator and key == "TARGET":
                target = value
        elif arg.startswith("--env=TARGET="):
            target = arg.removeprefix("--env=TARGET=")
    if not target:
        raise ScriptError("Не задан TARGET. Укажите TARGET в .env или передайте --env TARGET=<file>.tex.")
    return target


def pdf_from_target(target: str) -> str:
    target_path = Path(target)
    if target_path.suffix != ".tex":
        raise ScriptError(f"TARGET должен указывать на .tex файл, получено: {target}")
    return str(target_path.with_suffix(".pdf"))


def resolve_env_value(name: str, spec: object) -> str:
    if isinstance(spec, str):
        return spec
    if not isinstance(spec, dict):
        raise ScriptError(f"Некорректное значение env.{name} в diff_config.toml.")

    source_name = spec.get("from_env")
    default = spec.get("default")
    value = env_value(str(source_name)) if source_name else None
    if value is None:
        value = default
    if value is None:
        raise ScriptError(f"Не задана переменная {source_name} для env.{name}.")
    if not isinstance(value, str):
        raise ScriptError(f"Значение env.{name} должно быть строкой.")
    if spec.get("resolve") and value:
        value = str((PROJECT_DIR / value).resolve() if not Path(value).is_absolute() else Path(value).resolve())
    return value


def append_config_env(command: list[str], config: dict[str, Any]) -> None:
    env_config = config.get("env", {})
    if not isinstance(env_config, dict):
        raise ScriptError("В diff_config.toml параметр [diff_pdf.env] должен быть таблицей.")

    for name, spec in env_config.items():
        command.extend(["--env", f"{name}={resolve_env_value(name, spec)}"])


def append_copy_paths(command: list[str], config: dict[str, Any]) -> None:
    copy_config = config.get("copy", {})
    if not isinstance(copy_config, dict):
        raise ScriptError("В diff_config.toml параметр [diff_pdf.copy] должен быть таблицей.")
    paths = copy_config.get("paths", [])
    if not isinstance(paths, list):
        raise ScriptError("В diff_config.toml параметр diff_pdf.copy.paths должен быть списком.")

    for path in paths:
        command.extend(["--copy", string_value(path, name="diff_pdf.copy.paths[]")])


def build_command(config: dict[str, Any], extra_args: list[str]) -> list[str]:
    command = [
        "uvx",
        "diff-pdf-commits",
        "--build",
        string_value(config.get("build"), name="diff_pdf.build"),
    ]

    explicit_pdf = any(arg == "--pdf" or arg.startswith("--pdf=") for arg in extra_args)
    if not explicit_pdf:
        if config.get("pdf_from_target", False):
            command.extend(["--pdf", pdf_from_target(target_from_args(extra_args))])
        else:
            command.extend(["--pdf", string_value(config.get("pdf"), name="diff_pdf.pdf")])

    append_config_env(command, config)

    if config.get("view", False) and not any(arg in {"--view", "--no-view"} for arg in extra_args):
        command.append("--view")

    append_copy_paths(command, config)
    command.extend(extra_args)
    return command


def main() -> int:
    command = build_command(load_config(), sys.argv[1:])
    print(f"==> {' '.join(command)}", flush=True)
    return subprocess.run(command, cwd=PROJECT_DIR, check=False).returncode


if __name__ == "__main__":
    sys.exit(script_main(main))
