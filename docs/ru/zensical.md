# Документация

Документация лежит в `docs/` и собирается через Zensical. Основная версия - русская: она открывается по корневому адресу сайта. Английская версия лежит отдельно в `/en/`.

| Версия | Исходники | Конфиг | Куда собирается |
| --- | --- | --- | --- |
| Русская | `docs/ru/` | `zensical.toml` | `docs-site/` |
| Английская | `docs/en/` | `zensical.en.toml` | `docs-site/en/` |

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

Если меняете структуру или навигацию, сначала обновите `zensical.toml` для русской версии, затем внесите такие же изменения в `zensical.en.toml`.
