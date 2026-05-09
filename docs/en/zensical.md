# Documentation

Project documentation is built with Zensical and stored in `docs/`. The Russian version is stored in `docs/ru/`, and the English version is stored in `docs/en/`.

## Local run

Run documentation:

=== "Task"

    ```bash
    task docs
    ```

=== "Manual"

    ```bash
    docker compose --profile docs up docs
    ```

After startup, the site is available in the browser:

```text
http://localhost:8000
```

`task docs` first builds both language versions, then serves static files from `docs-site/`. After Markdown or config changes, restart the command.

For live reload, run one language version separately:

=== "Russian"

    ```bash
    task docs:serve:ru
    ```

=== "English"

    ```bash
    task docs:serve:en
    ```

Stop the service:

=== "Task"

    ```bash
    task docs:down
    ```

=== "Manual"

    ```bash
    docker compose --profile docs down
    ```

Download the documentation Docker image in advance:

=== "Task"

    ```bash
    task docs:pull
    ```

=== "Manual"

    ```bash
    docker compose --profile docs pull docs
    ```

## Bilingual build

The Russian site is built from `zensical.toml` into `docs-site/`. The English site is built from `zensical.en.toml` into `docs-site/en/`. Both configs define language alternatives, so the UI shows a language selector.

Build the static site:

=== "Task"

    ```bash
    task docs:build
    ```

=== "Manual"

    ```bash
    docker compose --profile docs run --rm docs "zensical build --config-file zensical.toml && zensical build --config-file zensical.en.toml"
    ```

## Image

Documentation uses the official image:

```text
zensical/zensical:0.0.40
```

Site settings are stored in `zensical.toml` and `zensical.en.toml`.
