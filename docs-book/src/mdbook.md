# Документация mdBook

## Локальный запуск

Запустить документацию:

```bash
docker compose --profile docs up
```

После запуска книга доступна в браузере:

```text
http://localhost:3000
```

Остановить сервис:

```bash
docker compose --profile docs down
```

Заранее скачать Docker-образ документации:

```bash
docker compose --profile docs pull
```

## Образ

Для документации используется компактный образ:

```text
peaceiris/mdbook@sha256:a82fd90af897238521c17e4b64479f5d56b578e4776198788256086b3a59617a
```