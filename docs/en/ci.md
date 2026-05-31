# CI/CD and releases

The repository uses GitHub Actions to check helper tools, build the PDF, publish release assets, and push generated PDFs to a separate archive repository.

## GitHub Pages

The `Publish Zensical docs` workflow builds bilingual documentation with `task docs:build:pages` and publishes `docs-site/` to GitHub Pages. This build uses `zensical.pages.toml` and `zensical.pages.en.toml` so language-switcher links and `site_url` point to the public Pages URL.

## Check tools

The `Release check tools exe` workflow runs on `v*` tag pushes and manually. It builds the Windows project-state checker:

- `diploma-latex-check.exe`;
- `SHA256SUMS.txt`.

The release publishing script is `scripts/ci/release_check_tools.py`, and the GitHub-specific Taskfile is `.github/tasks/check-tools-exe.yml`.

## PDF build and release

The PDF pipeline is split into two workflows:

- `Build PDF` builds the final PDF through Docker, downloads the current checktool assets, and uploads the `pdf-release-assets` artifact;
- `Release PDF` downloads the artifact from a successful `Build PDF` run and publishes the ready files to the GitHub Release and PDF archive.

For `v*` tags, the PDF build is not started directly by the tag push. `Build PDF` is triggered through `workflow_run` after `Release check tools exe` finishes successfully. This ensures that the artifact receives the current `checktool-windows-x64.exe` built for the same tag. After a successful build, `Release PDF` is triggered through `workflow_run` from `Build PDF`.

`Release PDF` can be rerun manually without rebuilding LaTeX: provide the `build_run_id` of a successful `Build PDF` run. The workflow downloads the saved artifact and repeats only the publishing steps.

The release assets are:

- `pdf-Куприянов_И221_диплом.pdf`;
- `checktool-windows-x64.exe`, if found in the release;
- `checktool-SHA256SUMS.txt`, if found in the release.

The check-tools workflow also leaves the original `diploma-latex-check.exe` and `SHA256SUMS.txt` assets. The PDF workflow adds the `checktool-` aliases so the checker assets are easier to distinguish from the PDF in the release asset list.

## PDF archive

After publishing the release, the `Release PDF` workflow pushes the PDF to the separate `ethercod3/diploma-pdf-archive` repository. That repository builds a static archive site for GitHub Pages with Material for MkDocs.

The main repository needs this GitHub Actions secret for archive access:

```text
PDF_ARCHIVE_TOKEN
```

The token must have `Contents: Read and write` for `ethercod3/diploma-pdf-archive`. The number of retained PDFs is controlled by the `PDF_ARCHIVE_MAX_BUILDS` repository variable; the default is `50`.

## Nightly

The nightly build is started by the `Build PDF` workflow at 04:00 Asia/Yakutsk. GitHub Actions cron uses UTC, so the schedule is `0 19 * * *`.

After a successful build, the `Release PDF` workflow publishes the result to the service tag and release `nightly`. The `scripts/ci/publish_pdf_release.py` script moves the `nightly` tag to the commit used for the artifact and reuploads the PDF asset.

## Backup

The `Backup git bundle` workflow runs manually and every Sunday at 05:00 Asia/Yakutsk. It creates a `git bundle`, uploads it through `rclone` to the configured cloud remotes, and keeps the latest 30 backup files.

The workflow requires this repository secret:

```text
RCLONE_CONFIG_CONTENT
```

The secret value is the full contents of `rclone.conf`. The default destinations are:

```text
gdrive:diploma_latex_backups,ydisk:diploma_latex_backups
```

They can be overridden with the `BACKUP_RCLONE_DESTINATIONS` repository variable. Details: [Backups](backup.md).

## CI caches

The Windows workflow for `diploma-latex-check.exe` enables the `uv` cache keyed by `uv.lock`. The `Build PDF` workflow uses `docker-compose.ci-cache.yaml`: Docker BuildKit stores build layers in GitHub Actions cache separately for `latex`, `docx`, `mermaid`, and `python`.

## Private code repository

To build appendices with application source code, the `Build PDF` workflow checks out the private repository `ethercod3/diploma_code` into `vault_diploma`. The LaTeX repository must have this GitHub Actions secret:

```text
VIEW_DIPLOMA_CODE
```

The token only needs read-only contents access to `ethercod3/diploma_code`.

The CI script `scripts/ci/prepare_pdf_release_env.py` creates `.env` with:

```env
VAULT_PATH="/vault_code"
VAULT_OS_PATH="./vault_diploma"
TARGET="Куприянов_И221_диплом.tex"
```

It also writes `HOST_UID` and `HOST_GID` so Docker containers can write to bind mounts as the GitHub runner user.

## CI scripts

Non-trivial workflow logic is kept in scripts:

| Script | Purpose |
| --- | --- |
| `scripts/ci/prepare_pdf_release_env.py` | Creates `.env` for the CI PDF build |
| `scripts/ci/resolve_pdf_release_context.py` | Resolves the release tag and checktool asset source |
| `scripts/ci/download_latest_checktool_assets.py` | Downloads checktool assets from the appropriate release |
| `scripts/ci/publish_pdf_release.py` | Creates/updates the release and uploads PDF/checktool assets |
| `scripts/ci/check_pdf_archive_access.nu` | Checks access to the PDF archive before publishing |
| `scripts/ci/publish_pdf_archive.nu` | Publishes the PDF to the separate archive repository |
| `scripts/ci/release_check_tools.py` | Publishes the project-state-checker exe |

Workflow YAML keeps only basic commands such as `python ...`, `nu ...`, and `task build`.
