"""Полная Docker-сборка всех публикуемых артефактов проекта.

Последовательно запускает Compose-профили для DOCX, Mermaid, Python-диаграмм
и LaTeX, останавливая цепочку на первом неуспешном профиле.
"""

from common import docker_compose_command, run_command, script_main

PROFILES = [
    ("docx", "docx_pdf"),
    ("mermaid", "mermaid_diagrams"),
    ("python", "python_diagrams"),
    ("latex", "latex"),
]


def run_profile(profile: str, service: str) -> int:
    print(f"\n==> {profile}", flush=True)
    result = run_command(
        [*docker_compose_command(), "--profile", profile, "run", "--build", "--rm", service],
        check=False,
    )

    return result.returncode


def main() -> int:
    for profile, service in PROFILES:
        exit_code = run_profile(profile, service)
        if exit_code != 0:
            return exit_code

    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
