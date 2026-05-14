# Документация

Документация лежит в `docs/` и собирается через Zensical. Основная версия - русская: она открывается по корневому адресу сайта. Английская версия лежит отдельно в `/en/`.

| Версия | Исходники | Конфиг | Куда собирается |
| --- | --- | --- | --- |
| Русская | `docs/ru/` | `zensical.toml` | `docs-site/` |
| Английская | `docs/en/` | `zensical.en.toml` | `docs-site/en/` |

Для публикации на GitHub Pages есть отдельные конфиги `zensical.pages.toml` и `zensical.pages.en.toml`. Они используют те же исходники, но задают абсолютный `site_url` для `https://ethercod3.github.io/diploma_latex/`.

## Локальный запуск

Собрать и запустить сайт с двумя языками:

=== "Task"

    ```bash
    task docs
    ```

=== "Ручной"

    ```bash
    docker compose --profile docs up docs
    ```

После запуска сайт доступен в браузере:

```text
http://localhost:8000
```

`task docs` сначала собирает русскую версию, затем английскую, а после этого раздает статические файлы из `docs-site/`. После изменения Markdown-файлов или конфигов команду нужно перезапустить.

## Двуязычная сборка

В обоих конфигах задан `extra.alternate`, поэтому при обычном `task docs` в интерфейсе появляется переключатель языка. Первым в списке указан русский язык.

Собрать статический сайт без запуска сервера:

=== "Task"

    ```bash
    task docs:build
    ```

=== "Ручной"

    ```bash
    docker compose --profile docs run --rm docs "zensical build --config-file zensical.toml && zensical build --config-file zensical.en.toml"
    ```

Собрать вариант для GitHub Pages:

=== "Task"

    ```bash
    task docs:build:pages
    ```

=== "Ручной"

    ```bash
    docker run --rm --entrypoint sh -v "$PWD:/data" -w /data zensical/zensical:0.0.40 -lc "zensical build --config-file zensical.pages.toml && zensical build --config-file zensical.pages.en.toml"
    ```

Остановить сервис:

=== "Task"

    ```bash
    task docs:down
    ```

=== "Ручной"

    ```bash
    docker compose --profile docs down
    ```

Заранее скачать Docker-образ документации:

=== "Task"

    ```bash
    task docs:pull
    ```

=== "Ручной"

    ```bash
    docker compose --profile docs pull docs
    ```

## Образ

Для документации используется официальный образ:

```text
zensical/zensical:0.0.40
```

Если меняете структуру или навигацию, сначала обновите `zensical.toml` для русской версии, затем внесите такие же изменения в `zensical.en.toml`, `zensical.pages.toml` и `zensical.pages.en.toml`.
