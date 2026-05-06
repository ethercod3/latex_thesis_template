# Быстрый старт

Соберите Docker-образы и запустите полную сборку:

```bash
docker compose --profile docx --profile mermaid --profile python --profile latex build
python scripts/build_all.py
```

Скрипт `scripts/build_all.py` запускает профили в порядке: `docx` \\(\\rightarrow\\) `mermaid` \\(\\rightarrow\\) `python` \\(\\rightarrow\\) `latex`.

Первый `build` будет долгим. Повторно выполнять `build` нужно только после изменения Dockerfile, зависимостей или базовых образов.

Если Docker-образы уже собраны, достаточно:

```bash
python scripts/build_all.py
```

Все вспомогательные Python-скрипты запускаются одинаково в Windows, Linux и macOS:

```bash
python scripts/build_all.py
python scripts/compile_mermaid.py
python scripts/compile_python_diagrams.py
```
