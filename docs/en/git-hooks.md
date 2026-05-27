# Git hooks

To automatically update final PDF checksums in README before each commit, enable local hooks:

=== "Task"

    ```bash
    task hooks
    ```

=== "Manual"

    ```bash
    git config core.hooksPath .githooks
    ```

The hook requires the Python package `python-dotenv`. It is listed in `pyproject.toml` and `uv.lock`.

If the environment is not prepared yet, install dependencies:

=== "Task"

    ```bash
    task deps
    ```

=== "Manual"

    ```bash
    uv sync
    ```

The hook calculates hashes of the current PDF using algorithms from the standard `hashlib` module.[^pdf-hash] If the PDF is missing, README is not changed and the commit continues with the old value.

[^pdf-hash]: Checksums identify a specific binary PDF, not the semantic state of the sources. Even small changes in metadata or build order can change the hash without a visible visual difference.
