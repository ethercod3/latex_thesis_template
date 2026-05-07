# Документация mdBook

## Локальный запуск

Запустить документацию:

```bash
task docs
```

Или вручную: `docker compose --profile docs up`.

После запуска книга доступна в браузере:

```text
http://localhost:3000
```

Остановить сервис:

```bash
task docs:down
```

Или вручную: `docker compose --profile docs down`.

Заранее скачать Docker-образ документации:

```bash
task docs:pull
```

Или вручную: `docker compose --profile docs pull`.

## Образ

Для документации используется компактный образ:

```text
peaceiris/mdbook@sha256:a82fd90af897238521c17e4b64479f5d56b578e4776198788256086b3a59617a
```
