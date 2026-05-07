# Документация mdBook

## Локальный запуск

Запустить документацию:

{{#tabs global="runmode"}}

{{#tab name="Task"}}

```bash
task docs
```

{{#endtab}}

{{#tab name="Ручной"}}

```bash
docker compose --profile docs up
```

{{#endtab}}

{{#endtabs}}

После запуска книга доступна в браузере:

```text
http://localhost:3000
```

Остановить сервис:

{{#tabs global="runmode"}}

{{#tab name="Task"}}

```bash
task docs:down
```

{{#endtab}}

{{#tab name="Ручной"}}

```bash
docker compose --profile docs down
```

{{#endtab}}

{{#endtabs}}

Заранее скачать Docker-образ документации:

{{#tabs global="runmode"}}

{{#tab name="Task"}}

```bash
task docs:pull
```

{{#endtab}}

{{#tab name="Ручной"}}

```bash
docker pull peaceiris/mdbook@sha256:a82fd90af897238521c17e4b64479f5d56b578e4776198788256086b3a59617a
```

{{#endtab}}

{{#endtabs}}

## Вкладки

Для переключения между вариантами команд используется препроцессор `mdbook-tabs`.
При запуске через Docker ассеты вкладок подготавливаются автоматически перед `mdbook serve`.

Для локального запуска без Docker:

{{#tabs global="runmode"}}

{{#tab name="Task"}}

```bash
cargo install mdbook-tabs
task docs:tabs
mdbook serve docs-book
```

{{#endtab}}

{{#tab name="Ручной"}}

```bash
cargo install mdbook-tabs
cd docs-book
mdbook-tabs install
mdbook serve
```

{{#endtab}}

{{#endtabs}}

## Образ

Для документации используется компактный образ:

```text
peaceiris/mdbook@sha256:a82fd90af897238521c17e4b64479f5d56b578e4776198788256086b3a59617a
```
