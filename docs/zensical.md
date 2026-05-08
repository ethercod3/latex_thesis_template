# Документация

Документация проекта собирается через Zensical и лежит в `docs/`.

## Локальный запуск

Запустить документацию:

=== "Task"

    ```bash
    task docs
    ```

=== "Ручной"

    ```bash
    docker compose --profile docs up
    ```

После запуска сайт доступен в браузере:

```text
http://localhost:8000
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

Настройки сайта находятся в `zensical.toml`.
