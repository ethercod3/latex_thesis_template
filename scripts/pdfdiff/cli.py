"""CLI для сравнения PDF между git-коммитами."""

from __future__ import annotations

import click
from click.core import ParameterSource

from .config import DiffPdfConfig, parse_profiles, requested_save_path, target_pdf_name
from .runner import PdfDiffRunner


@click.command(context_settings={"help_option_names": ["--help"]})
@click.argument("left_commit")
@click.argument("right_commit")
@click.option(
    "--pdf",
    default=None,
    help="Имя PDF-файла для сравнения. По умолчанию берется TARGET из .env с расширением .pdf.",
)
@click.option(
    "--keep",
    is_flag=True,
    help="Оставить временную папку .pdf_diff после завершения diff-pdf.",
)
@click.option(
    "--view",
    is_flag=True,
    help="Открыть визуальное сравнение в diff-pdf. Используется по умолчанию, если не указан --save.",
)
@click.option(
    "--save",
    default=None,
    is_flag=False,
    flag_value=None,
    type=str,
    hidden=True,
)
@click.option(
    "--profiles",
    default="all",
    metavar="PROFILES",
    help=(
        "Профили Docker для запуска перед сравнением. Можно указать готовую группу "
        "all, docx, mermaid, latex или список через запятую, например mermaid,python. "
        "Профиль latex добавляется автоматически, если его нет в списке."
    ),
)
@click.pass_context
def main(
    ctx: click.Context,
    left_commit: str,
    right_commit: str,
    pdf: str | None,
    keep: bool,
    view: bool,
    save: str | None,
    profiles: str,
) -> None:
    try:
        profiles_list = parse_profiles(profiles)
    except ValueError as error:
        raise click.BadParameter(str(error)) from error

    pdf_name = pdf or target_pdf_name()
    save_source = ctx.get_parameter_source("save")
    save_arg: str | bool = save if save_source == ParameterSource.COMMANDLINE and save is not None else False
    if save_source == ParameterSource.COMMANDLINE and save is None:
        save_arg = True
    effective_view = view or not save_arg

    config = DiffPdfConfig(
        left_commit=left_commit,
        right_commit=right_commit,
        pdf_name=pdf_name,
        profiles=profiles_list,
        keep=keep,
        view=effective_view,
        save_path=requested_save_path(save_arg, left_commit, right_commit, pdf_name),
    )
    raise SystemExit(PdfDiffRunner(config).run())


def run() -> None:
    main.main(prog_name="diff_pdf_commits.py", standalone_mode=True)
