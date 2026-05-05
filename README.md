# Исходники диплома

<!-- DIPLOMA_SHA256_START -->
## Контрольная сумма PDF

**Файл:** `Куприянов_И221_диплом.pdf`

**SHA-256:** `32a07f44efac636d8b4f280b3a2489e66bb257baf981e8963f0aa61ff33031c9`
<!-- DIPLOMA_SHA256_END -->

[![GitHub last commit](https://img.shields.io/github/last-commit/ethercod3/diploma_latex?style=flat-square&logo=github)](https://github.com/ethercod3/diploma_latex/commits)
[![GitHub repo size](https://img.shields.io/github/repo-size/ethercod3/diploma_latex?style=flat-square&logo=github)](https://github.com/ethercod3/diploma_latex)
![LaTeX](https://img.shields.io/badge/LaTeX-LuaLaTeX-008080?style=flat-square&logo=latex)
![latexmk](https://img.shields.io/badge/Build-latexmk-008080?style=flat-square&logo=latex)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Charts-Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Mermaid](https://img.shields.io/badge/Diagrams-Mermaid-FF3670?style=flat-square&logo=mermaid&logoColor=white)

Репозиторий с исходниками дипломной работы: `LaTeX`-документы, `Mermaid`-диаграммы, Python-диаграммы, DOCX-шаблоны титульных страниц и Docker-профили для воспроизводимой сборки.

## Что внутри

| Путь | Назначение |
| --- | --- |
| `*.tex`, `preamble/` | LaTeX-документы и настройки преамбулы |
| `docx/` | DOCX-исходники титульника и задания |
| `mermaid/` | Исходники Mermaid-диаграмм |
| `python_diagrams/` | Python-скрипты генерации диаграмм |
| `figures/` | Сгенерированные изображения и PDF для вставки в документ |
| `scripts/` | Вспомогательные скрипты сборки, конвертации и сравнения PDF |
| `docker/` | Dockerfile для отдельных профилей сборки |

## Git hooks

Чтобы перед каждым коммитом автоматически обновлялась SHA-256 итогового PDF в README, подключите локальные hooks:

```bash
git config core.hooksPath .githooks
```

Hook считает hash текущего PDF. Если PDF отсутствует, README не меняется и коммит продолжается со старым значением.

## Быстрый старт

```bash
python scripts/build_all.py
```

Макисмальная воспроизводимость с оригиналом будет, если вы будете собирать `Mermaid`-диаграммы из-под `Windows`. Если собирать их Docker-ом, то шрифт для `KaTex` (математических) выражений будет отличаться от оригинала. Если это для вас неважно, просто пользуйтесь скриптом выше.

Для запуска скрипта потребуется Docker. Если вы не планируете использовать Docker, для вас есть инструкции по ручной сборке всего, что есть в проекте.

## Навигация

- [Как скомпилировать проект вручную](#как-скомпилировать-проект-вручную)
- [Компиляция в Docker](#компиляция-в-docker)
- [Git hooks](#git-hooks)
- [Сравнение PDF между коммитами](#сравнение-pdf-между-коммитами)
- [Проблемы с компиляцией](#проблемы-с-компиляцией)
- [Как работать с диаграммами](#как-работать-с-диаграммами)
- [Генерация диаграмм Python](#генерация-диаграмм-python-вручную)

## Как скомпилировать проект вручную

1. Установить дистрибутив `LaTeX`. Под Windows рекомендуется установить `TexLive`. Установка долгая, но все пакеты сразу скачаются вместе с дистрибутивом. Компилятор в работе использовался `LuaTex`
2. Клонировать репозиторий
3. Скомпилировать файл: 

    ```bash
    lualatex -synctex=1 -interaction=nonstopmode "<файл>".tex
    ```

## Компиляция в Docker

1. Создайте в корне проекте файл `.env`

    Наполните его содержимое:

    ```
    VAULT_PATH="путь монтирования"
    VAULT_OS_PATH="фактический путь до кода на устройстве"
    TARGET="файл латеха"
    ```

    Пример:

    ```
    VAULT_PATH="/vault_code"
    VAULT_OS_PATH="../vault_diploma"
    TARGET="Куприянов_И221_диплом.tex"
    ```

    Пояснение:

    - `VAULT_PATH`: любой абсолютный unix путь. 
    - `VAULT_OS_PATH`: где относительно текущей папки лежит код
    - `TARGET`: `.tex` файл

2. Запустите компиляцию:

    ```bash
    docker compose --profile latex up --build
    ```

Первый билд будет долгим

### Профили Docker Compose

В проекте доступны профили:

- `latex` - компиляция LaTeX-документа
- `mermaid` - генерация Mermaid-диаграмм в `figures`
- `python` - генерация Python-диаграмм в `figures`
- `docx` - конвертация файлов `docx/*.docx` в одноименные PDF в корне проекта

Запуск отдельных профилей:

```bash
docker compose --profile latex up --build
docker compose --profile mermaid up --build
docker compose --profile python up --build
docker compose --profile docx up --build
```

Запуск всех профилей одной командой:

```bash
docker compose --profile docx --profile mermaid --profile python --profile latex up --build
```

При запуске всех профилей Docker Compose стартует сервисы вместе. Если нужно гарантированно собрать документ уже со свежими PDF из DOCX и диаграммами, сначала запустите профили `docx`, `mermaid` и `python`, затем профиль `latex`.

Последовательный запуск всех профилей уже вынесен в скрипты:

```bash
python scripts/build_all.py
```

Скрипты запускают профили в порядке `docx` -> `mermaid` -> `python` -> `latex` и останавливаются на первой ошибке.

Все вспомогательные скрипты проекта написаны на Python и запускаются одинаково в Windows, Linux и macOS:

```bash
python scripts/build_all.py
python scripts/compile_mermaid.py
python scripts/compile_python_diagrams.py
```

Скрипт `scripts/convert_docx_to_pdf.py` обычно запускается внутри Docker-профиля `docx`, потому что ему нужны LibreOffice, Ghostscript и qpdf.

### Сравнение PDF между коммитами

![pdf_diff_example](./github_images/pdf_diff_example.png)

Если нужно посмотреть визуальную разницу между двумя версиями диплома, используйте скрипт:

```bash
python scripts/diff_pdf_commits.py <commit_1> <commit_2>
```

Скрипт принимает 2 хэша коммита, по очереди переключается на каждый из них, собирает PDF через Docker, складывает две версии во временную папку и открывает `diff-pdf`.

Результат можно только открыть, только сохранить или сделать оба действия:

```bash
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --view
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --save
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --view --save
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --save path/to/diff.pdf
```

Без `--view` и `--save` скрипт открывает diff. При `--save` без пути результат сохраняется в `.pdf_diff/saved`.

Скачать `diff-pdf` можно в [репозитории](https://github.com/vslavik/diff-pdf/)

По умолчанию запускаются все профили в порядке `docx` -> `mermaid` -> `python` -> `latex`. Если нужно ограничить сборку, передайте опцию `--profiles`:

```bash
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles all
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles docx
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles mermaid
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles latex
```

Пояснение:

- `all`: `docx` -> `mermaid` -> `python` -> `latex`
- `docx`: `docx` -> `latex`
- `mermaid`: `mermaid` -> `latex`
- `latex`: только `latex`

Перед запуском рабочее дерево Git должно быть чистым. После завершения скрипт возвращается на исходный `HEAD`, удаляет временные файлы и восстанавливает текущие файлы из `figures`, а также PDF в корне проекта, например `титульник.pdf` и `задание.pdf`.

## Проблемы с компиляцией

**ВАЖНО**: компилируйте по 2 раза минимум. В первую компиляцию могут быть ошибки, так как `LaTeX` будет создавать вспомогательные файлы со счетчиками (счетчик библиографии, таблиц, рисунков.) Во вторую компиляцию `LaTeX` их подтянет.

**ВАЖНО 2**: если не компилируется:

Запустите команду из `cmd`, не из `powershell`. Если не сработало:

1. Переименуйте `.tex` файл в `main.tex` (или любое другое название на латинице)

2. Используйте следующую команду для компиляции:

    ```bash
    lualatex main.tex
    ```

### О титульнике

`LaTeX` вставит титульник из файла `титульник.pdf` в начало файла. Поэтому он должен быть в проекте перед компиляцией (как и все рисунки, листинги). В проекте есть `docx/титульник.docx` и `docx/задание.docx`; их можно конвертировать через Docker:

```bash
docker compose --profile docx up --build
```

Профиль берет все файлы `docx/*.docx` и складывает одноименные PDF в корень проекта, например `docx/титульник.docx` -> `титульник.pdf`.

При конвертации профиль пропускает пустые страницы. Если нужно сохранить PDF как есть, запустите профиль с переменной `SKIP_BLANK_PAGES=0`:

```bash
docker compose --profile docx run --rm -e SKIP_BLANK_PAGES=0 docx_pdf
```

Альтернативный вариант - открыть DOCX в Microsoft Word и экспортировать его в PDF вручную: `Файл` -> `Экспорт` -> `Создать PDF/XPS`. Для титульника и задания нужно сохранить PDF в корень проекта с именами `титульник.pdf` и `задание.pdf`.

### Если нет кода

Если у вас нет файлов кода, и вы хотите скомпилировать проект без них, закомментируйте эти строки в конце `.tex` файл (в `latex` комментарии - все строки, содержащие `%` в начале)

```latex
\newpage
\input{appendix_b.tex}
\newpage
\input{include_listings.tex}
```

### Если есть код

Положите код на одном уровне с папкой `LaTeX` кода. При компиляции `LaTeX` обращается по такому пути:

`../vault_diploma/<файл>`

## Как работать с диаграммами

### Сборка вручную

Чтобы пересобрать диаграмму в `pdf`:

1. Отредактируйте нужную диаграмму (они содержатся в файлах `.mmdc`)
2. Установите инструмент командой строки `mmdc` : https://github.com/mermaid-js/mermaid-cli
3. Пересоберите диаграмму:
    
    ```bash
    mmdc -i <file.mmdc> -o <file.pdf> -f
    ```

    флаг `-f` нужен для того, чтобы лист pdf обрезался под размер диаграммы

### Автоматическая сборка всех диаграмм

Запустите скрипт `scripts/compile_mermaid.py` в проекте. Этот скрипт автоматически прогонит все файлы из папки `mermaid` и положит результат в папку `figures`

```bash
python scripts/compile_mermaid.py
```

### Сборка через Docker

```
docker compose --profile mermaid up --build
```

## Генерация диаграмм Python вручную

1. Установите интерпретатор `python` (использовалась версия `3.13+`)
2. Установите в окружение библиотеки: `pip install -r requirements.txt`
3. Теперь вы можете запустить скрипт и получить на выходе файл диаграммы

    ```bash
    python scripts/compile_python_diagrams.py
    ```

## Генерация диаграмм Python через Docker

```bash
docker compose --profile python up --build
```
