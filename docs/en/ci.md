# CI/CD and releases

The repository uses GitHub Actions to check helper tools, build the PDF, and publish release assets.

## Check tools

The `Release check tools exe` workflow runs on `v*` tag pushes and manually. It builds the Windows environment checker:

- `diploma-latex-check.exe`;
- `SHA256SUMS.txt`.

The release publishing script is `scripts/ci/release_check_tools.py`, and the GitHub-specific Taskfile is `.github/tasks/check-tools-exe.yml`.

## PDF release

The `Release PDF` workflow builds the final PDF through Docker and uploads it to a GitHub Release.

For `v*` tags, the PDF workflow is not started directly by the tag push. It is triggered through `workflow_run` after `Release check tools exe` finishes successfully. This ensures that the release receives the current `checktool-windows-x64.exe` built for the same tag.

The release assets are:

- `pdf-Куприянов_И221_диплом.pdf`;
- `checktool-windows-x64.exe`, if found in the release;
- `checktool-SHA256SUMS.txt`, if found in the release.

The check-tools workflow also leaves the original `diploma-latex-check.exe` and `SHA256SUMS.txt` assets. The PDF workflow adds the `checktool-` aliases so the checker assets are easier to distinguish from the PDF in the release asset list.

## Nightly

The nightly build runs at 04:00 Asia/Yakutsk. GitHub Actions cron uses UTC, so the schedule is `0 19 * * *`.

The nightly build is published to the service tag and release `nightly`. The `scripts/ci/publish_pdf_release.py` script moves the `nightly` tag to the current default-branch commit and reuploads the PDF asset.

## Private code repository

To build appendices with application source code, the workflow checks out the private repository `ethercod3/diploma_code` into `vault_diploma`. The LaTeX repository must have this GitHub Actions secret:

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

Non-trivial workflow logic is kept in Python scripts:

| Script | Purpose |
| --- | --- |
| `scripts/ci/prepare_pdf_release_env.py` | Creates `.env` for the CI PDF build |
| `scripts/ci/resolve_pdf_release_context.py` | Resolves the release tag and checktool asset source |
| `scripts/ci/download_latest_checktool_assets.py` | Downloads checktool assets from the appropriate release |
| `scripts/ci/publish_pdf_release.py` | Creates/updates the release and uploads PDF/checktool assets |
| `scripts/ci/release_check_tools.py` | Publishes the environment-checker exe |

Workflow YAML keeps only basic commands such as `python ...` and `task build`.
