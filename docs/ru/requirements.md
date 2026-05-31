# Что нужно установить

Набор инструментов зависит от того, как вы собираете проект.

| Инструмент | Когда нужен | Как проверить |
| --- | --- | --- |
| mise | Опциональная установка Python, uv и Task в версиях проекта | `mise --version` |
| Task | Рекомендуемый запуск команд проекта | `task --version` |
| Docker | Полная воспроизводимая сборка, Zensical, DOCX-конвертация | `docker --version` |
| Python | Локальная компиляция LaTeX через PyLuaTeX и ручной запуск вспомогательных скриптов | `python --version` |
| uv | Синхронизация и запуск Python-зависимых задач проекта | `uv --version` |
| TeX Live | Локальная сборка LaTeX без Docker | `lualatex --version` |
| latexmk | Быстрая локальная сборка LaTeX | `latexmk --version` |
| biber | Библиография при локальной сборке | `biber --version` |
| Mermaid CLI | Локальная сборка Mermaid-диаграмм | `mmdc --version` |
| pdfcrop | Обрезка PDF после локальной сборки Mermaid | `pdfcrop --version` |
| Ghostscript | Нужен `pdfcrop`, DOCX-конвертации и анализ цветности страниц PDF | `gs --version` |
| qpdf | Извлечение страниц PDF без изменения поворота и геометрии | `qpdf --version` |
| diff-pdf | Визуальное сравнение PDF между коммитами | `diff-pdf --help` |
| rclone | Резервное копирование `git bundle` в облачные хранилища | `rclone version` |

!!! tip "Самый короткий путь"
    Если установлен mise, выполните `mise trust`, `mise install`, `mise run setup` и `mise run check`. Если mise не используется, установите Task и Docker, затем выполните команды из раздела [Быстрый старт](quick-start.md).

!!! tip "Проверка состояния проекта"
    После установки инструментов можно запустить `task check`. Команда проверит `.env`, целевой `.tex`, путь к коду приложения, титульные PDF и актуальность диаграмм.

    Если Python еще не установлен и нужно только проверить состояние проекта, скачайте `diploma-latex-check.exe` из GitHub Releases, положите файл в корень проекта и запустите:

    ```powershell
    .\diploma-latex-check.exe
    ```

    Такая проверка не требует Python для запуска самого скрипта, но локальная сборка LaTeX без Docker все равно потребует Python, потому что документ использует PyLuaTeX.

!!! note "Локальная сборка без Docker"
    Для сборки без Docker нужны TeX Live, Python, `latexmk`, `lualatex` и `biber`. Под Windows `latexmk` и `biber` обычно ставятся вместе с TeX Live. Python нужен не только вспомогательным скриптам: LaTeX-документ использует PyLuaTeX и запускает команду `python` во время компиляции.

!!! note "PDF crop без Docker"
    Для локальных команд `task mermaid` и `task crop -- path/to/file.pdf` нужны `pdfcrop` и Ghostscript. Если нужна генерация Mermaid без обрезки полей, запустите `task mermaid -- --no-crop`. Если локальных зависимостей нет, используйте Docker-профили `task mermaid:docker` или `task crop:docker -- path/to/file.pdf`.

!!! note "Разделение PDF на цветные и ЧБ страницы"
    Команда `task pdf:split-color -- path/to/file.pdf` запускается в LaTeX Docker-образе. Внутри контейнера Ghostscript определяет цветные страницы через `inkcov`, а `qpdf` экспортирует выбранные страницы в `*_color.pdf` и `*_bw.pdf` без перерисовки исходных страниц.

!!! note "Тесты скриптов"
    Python-зависимости из `pyproject.toml` и `uv.lock` включают `pytest`. После `task deps` можно проверить вспомогательные скрипты командой `task python:test`.

## Частые сценарии

| Что нужно сделать | Куда идти |
| --- | --- |
| Собрать итоговый PDF | [Быстрый старт](quick-start.md) |
| Собрать без Docker | [Сборка без Docker](manual-build.md) |
| Настроить TeXstudio | [Настройка TeXstudio](texstudio.md) |
| Пересобрать титульник и задание | [Титульник и задание](title-pages.md) |
| Пересобрать диаграммы | [Диаграммы](diagrams.md) |
| Подключить код приложения | [Код в приложениях](source-code.md) |
| Сравнить PDF между коммитами | [Сравнение PDF между коммитами](pdf-diff.md) |
| Разделить PDF на цветные и ЧБ страницы | [Разделение PDF на цветные и ЧБ страницы](pdf-color-split.md) |
| Настроить резервное копирование | [Резервное копирование](backup.md) |
| Разобрать ошибку сборки | [Проблемы с компиляцией](troubleshooting.md) |
| Проверить CI/CD и релизные артефакты | [CI/CD и релизы](ci.md) |
