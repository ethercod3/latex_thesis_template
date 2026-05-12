# Documentation

Project documentation is stored in `docs/` and built with Zensical. The Russian version is the primary site and opens at the root URL. The English version is served separately from `/en/`.

| Version | Sources | Config | Build output |
| --- | --- | --- | --- |
| Russian | `docs/ru/` | `zensical.toml` | `docs-site/` |
| English | `docs/en/` | `zensical.en.toml` | `docs-site/en/` |

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

## Bilingual build

Both configs define `extra.alternate`, so the regular `task docs` UI shows a language selector. Russian is listed first.

Build the static site without starting the server:

=== "Task"

    ```bash
    task docs:build
    ```

=== "Manual"

    ```bash
    docker compose --profile docs run --rm docs "zensical build --config-file zensical.toml && zensical build --config-file zensical.en.toml"
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

## Image

Documentation uses the official image:

```text
zensical/zensical:0.0.40
```

If you change structure or navigation, update `zensical.toml` for the Russian version first, then mirror the same changes in `zensical.en.toml`.
