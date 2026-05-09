# Документация

Документация проекта собирается через Zensical и лежит в `docs/`. Русская версия находится в корне `docs/`, английская - в `docs/en/`.

## Локальный запуск

Собрать и запустить двуязычный сайт:

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

`task docs` сначала собирает обе языковые версии, а затем раздает статические файлы из `docs-site/`. После изменений Markdown или конфигов перезапустите команду.

Для режима live reload можно запустить одну языковую версию отдельно:

=== "Русский"

    ```bash
    task docs:serve:ru
    ```

=== "English"

    ```bash
    task docs:serve:en
    ```

## Двуязычная сборка

Русский сайт собирается из `zensical.toml` в `docs-site/`. Английский сайт собирается из `zensical.en.toml` в `docs-site/en/`. В обоих конфигах задан `extra.alternate`, поэтому в UI появляется переключатель языка.

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

Настройки сайта находятся в `zensical.toml` и `zensical.en.toml`.
