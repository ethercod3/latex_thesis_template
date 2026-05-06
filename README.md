# Исходники диплома

[![GitHub last commit](https://img.shields.io/github/last-commit/ethercod3/diploma_latex?style=flat-square&logo=github)](https://github.com/ethercod3/diploma_latex/commits)
[![GitHub repo size](https://img.shields.io/github/repo-size/ethercod3/diploma_latex?style=flat-square&logo=github)](https://github.com/ethercod3/diploma_latex)
![LaTeX](https://img.shields.io/badge/LaTeX-LuaLaTeX-008080?style=flat-square&logo=latex)
![latexmk](https://img.shields.io/badge/Build-latexmk-008080?style=flat-square&logo=latex)
![biblatex](https://img.shields.io/badge/Bibliography-biblatex-008080?style=flat-square&logo=latex)
![biber](https://img.shields.io/badge/Backend-biber-008080?style=flat-square&logo=latex)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Charts-Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Mermaid](https://img.shields.io/badge/Diagrams-Mermaid-FF3670?style=flat-square&logo=mermaid&logoColor=white)

<!-- DIPLOMA_HASHES_START -->
## Контрольные суммы PDF

MD5: `a9a3ca825697f36ee44435995531cbb4`<br>
SHA-1: `af164523f4f7721ded42597523e7be5d50c4920d`<br>
SHA-256: `c3d42af399de10f36dc7d29437620803530d551a6b51dfad2e35fcfbec950e5c`<br>
SHA3-256: `a6bf05b5d5f7bf5786028991f5f3e0f8093458a936b01d22381f745b4fba51ae`<br>
BLAKE2s: `bf632dcf98eee42570b3f78ec8eaeb78ad94db0e270f86a8f38e2ee17c16ac01`<br>
SHAKE-128 (256-bit output): `e7272e380c1da03f5d2669cbc0d1e1760332afa89445464dfa3d7be9e190676b`<br>
<!-- DIPLOMA_HASHES_END -->

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

## Быстрый старт

```bash
docker compose --profile docx --profile mermaid --profile python --profile latex build
python scripts/build_all.py
```

Макисмальная воспроизводимость с оригиналом будет, если вы будете собирать `Mermaid`-диаграммы из-под `Windows`. Если собирать их Docker-ом, то шрифт для `KaTeX` (математических) выражений будет отличаться от оригинала. Если это для вас неважно, просто пользуйтесь скриптом выше.

Для запуска скрипта потребуется Docker. Если вы не планируете использовать Docker, для вас есть инструкции по ручной сборке всего, что есть в проекте.

## Навигация

- [Как скомпилировать проект вручную](#как-скомпилировать-проект-вручную)
- [Настройка TeXstudio](#настройка-texstudio)
- [Компиляция в Docker](#компиляция-в-docker)
- [Сравнение PDF между коммитами](#сравнение-pdf-между-коммитами)
- [Проблемы с компиляцией](#проблемы-с-компиляцией)
- [О титульнике](#о-титульнике)
- [Если нет кода](#если-нет-кода)
- [Если есть код](#если-есть-код)
- [Как работать с диаграммами](#как-работать-с-диаграммами)
- [Git hooks](#git-hooks)

## Как скомпилировать проект вручную

1. Установить дистрибутив `LaTeX`. Под Windows рекомендуется установить `TexLive`. Установка долгая, но все пакеты сразу скачаются вместе с дистрибутивом. Компилятор в работе использовался `LuaTex`
2. Клонировать репозиторий
3. Установить Python-зависимости для скриптов:

    ```bash
    pip install -r requirements.txt
    ```

4. Создать в корне проекта файл `.env` и указать в нем основной `.tex` файл:

    ```env
    TARGET="Куприянов_И221_диплом.tex"
    ```

5. Запустить ручную сборку через скрипт:

    ```bash
    python scripts/build_latex_manual.py
    ```

    Скрипт читает `TARGET` из `.env` через `python-dotenv`, создает `.aux_files`, запускает `lualatex`, затем `biber`, затем еще два раза `lualatex`. Итоговый PDF копируется из `.aux_files` в корень проекта.

    Если нужно собрать другой файл без изменения `.env`, передайте его явно:

    ```bash
    python scripts/build_latex_manual.py --target "<файл>.tex"
    ```

### Ручная компиляция без скрипта

1. Создать папку для вспомогательных файлов:

    ```bash
    mkdir .aux_files
    ```

    Если папка уже есть, этот шаг можно пропустить.

2. Скомпилировать файл. Так как проект использует `biblatex` с backend `biber`, одного запуска `lualatex` недостаточно:

    ```bash
    lualatex -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "<файл>.tex"
    biber ".aux_files/<файл>.bcf"
    lualatex -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "<файл>.tex"
    lualatex -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "<файл>.tex"
    ```

    Для основного файла проекта:

    ```bash
    lualatex -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "Куприянов_И221_диплом.tex"
    biber ".aux_files/Куприянов_И221_диплом.bcf"
    lualatex -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "Куприянов_И221_диплом.tex"
    lualatex -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "Куприянов_И221_диплом.tex"
    ```

    После сборки итоговый PDF окажется в `.aux_files`. Его нужно перенести в корень проекта:

    ```bash
    mv ".aux_files/<файл>.pdf" .
    ```

    В Windows `cmd` для основного файла:

    ```bat
    move ".aux_files\Куприянов_И221_диплом.pdf" .
    ```

## Настройка TeXstudio

Проект использует `LuaLaTeX` и `biblatex` с backend `biber`, поэтому в TeXstudio нужно настроить сборку без `BibTeX` и без `latexmk`.

1. Откройте `Options` $\rightarrow$ `Configure TeXstudio` $\rightarrow$ `Commands`.
2. В поле `LuaLaTeX` укажите:

    ```text
    lualatex -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" %.tex
    ```

3. В поле `Biber` укажите:

    ```text
    biber ".aux_files/%.bcf"
    ```

4. Откройте `Options` $\rightarrow$ `Configure TeXstudio` $\rightarrow$ `Build`.
5. В `Default Compiler` выберите `LuaLaTeX`.
6. В `Default Bibliography Tool` выберите `Biber`.
7. В `Build & View` выберите `User` и укажите последовательность:

    ```text
    txs:///lualatex | txs:///biber | txs:///lualatex | txs:///lualatex | txs:///view-pdf
    ```

Перед первой сборкой создайте папку `.aux_files` в корне проекта, если ее еще нет. Если TeXstudio не открывает PDF автоматически, откройте файл из `.aux_files` или перенесите его в корень проекта так же, как описано в ручной сборке.

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

2. Соберите LaTeX-образ:

    ```bash
    docker compose --profile latex build
    ```

3. Запустите компиляцию:

    ```bash
    docker compose --profile latex up
    ```

    Профиль `latex` запускает скрипт `scripts/build_latex_docker.py`. Он читает `TARGET` из переменных окружения, собирает документ через `lualatex`, `biber`, `lualatex`, `lualatex`, складывает временные файлы в `.aux_files_docker` и копирует готовый PDF в корень проекта.

Первый build будет долгим. Повторно выполнять `build` нужно только после изменения Dockerfile, зависимостей или базовых образов.

### Сборка Docker-образов

Собрать все Docker-образы проекта:

```bash
docker compose --profile docx --profile mermaid --profile python --profile latex build
```

Собрать образ отдельного профиля:

```bash
docker compose --profile latex build
docker compose --profile mermaid build
docker compose --profile python build
docker compose --profile docx build
```

Скрипты `scripts/build_all.py` и `scripts/diff_pdf_commits.py` не пересобирают образы при каждом запуске. Если Docker-образов еще нет, сначала выполните `build`.

### Профили Docker Compose

В проекте доступны профили:

- `latex` - компиляция LaTeX-документа
- `mermaid` - генерация Mermaid-диаграмм в `figures`
- `python` - генерация Python-диаграмм в `figures`
- `docx` - конвертация файлов `docx/*.docx` в одноименные PDF в корне проекта

Запуск отдельных профилей:

```bash
docker compose --profile latex up
docker compose --profile mermaid up
docker compose --profile python up
docker compose --profile docx up
```

Запуск всех профилей одной командой:

```bash
docker compose --profile docx --profile mermaid --profile python --profile latex up
```

При запуске всех профилей Docker Compose стартует сервисы вместе. Если нужно гарантированно собрать документ уже со свежими PDF из DOCX и диаграммами, сначала запустите профили `docx`, `mermaid` и `python`, затем профиль `latex`.

Последовательный запуск всех профилей уже вынесен в скрипты:

```bash
python scripts/build_all.py
```

Скрипты запускают профили в порядке `docx` $\rightarrow$ `mermaid` $\rightarrow$ `python` $\rightarrow$ `latex` и останавливаются на первой ошибке.
Перед первым запуском скрипта соберите образы командой из раздела [Сборка Docker-образов](#сборка-docker-образов).

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

По умолчанию запускаются все профили в порядке `docx` $\rightarrow$ `mermaid` $\rightarrow$ `python` $\rightarrow$ `latex`. Если нужно ограничить сборку, передайте опцию `--profiles`:

```bash
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles all
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles docx
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles mermaid
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles latex
```

Пояснение:

- `all`: `docx` $\rightarrow$ `mermaid` $\rightarrow$ `python` $\rightarrow$ `latex`
- `docx`: `docx` $\rightarrow$ `latex`
- `mermaid`: `mermaid` $\rightarrow$ `latex`
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
docker compose --profile docx up
```

Профиль берет все файлы `docx/*.docx` и складывает одноименные PDF в корень проекта, например `docx/титульник.docx` $\rightarrow$ `титульник.pdf`.

При конвертации профиль пропускает пустые страницы. Если нужно сохранить PDF как есть, запустите профиль с переменной `SKIP_BLANK_PAGES=0`:

```bash
docker compose --profile docx run --rm -e SKIP_BLANK_PAGES=0 docx_pdf
```

Альтернативный вариант - открыть DOCX в Microsoft Word и экспортировать его в PDF вручную: `Файл` $\rightarrow$ `Экспорт` $\rightarrow$ `Создать PDF/XPS`. Для титульника и задания нужно сохранить PDF в корень проекта с именами `титульник.pdf` и `задание.pdf`.

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

### Просмотр Mermaid-файлов на GitHub

GitHub не всегда показывает содержимое файлов Mermaid с расширением `.mmd` как обычный текстовый код. Если вместо исходника отображается предпросмотр или файл не открывается удобным образом, нажмите кнопку `View raw` на странице файла. Так GitHub откроет исходный `.mmd`-код диаграммы без обработки.

### Сборка вручную

Чтобы пересобрать диаграмму в `pdf`:

1. Отредактируйте нужную диаграмму (они содержатся в файлах `.mmd`)
2. Установите инструмент командой строки `mmdc` : https://github.com/mermaid-js/mermaid-cli
3. Пересоберите диаграмму:
    
    ```bash
    mmdc -i <file.mmd> -o <file.pdf> -f
    ```

    флаг `-f` нужен для того, чтобы лист pdf обрезался под размер диаграммы

### Автоматическая сборка всех диаграмм

Запустите скрипт `scripts/compile_mermaid.py` в проекте. Этот скрипт автоматически прогонит все файлы из папки `mermaid` и положит результат в папку `figures`

```bash
python scripts/compile_mermaid.py
```

### Сборка через Docker

```
docker compose --profile mermaid up
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
docker compose --profile python up
```

## Git hooks

Чтобы перед каждым коммитом автоматически обновлялись контрольные суммы итогового PDF в README, подключите локальные hooks:

```bash
git config core.hooksPath .githooks
```

Для работы hook нужен Python-пакет `python-dotenv`. Он уже указан в `requirements.txt`; если окружение еще не подготовлено, установите зависимости:

```bash
pip install -r requirements.txt
```

Hook считает хэши текущего PDF алгоритмами из стандартного `hashlib`. Если PDF отсутствует, README не меняется и коммит продолжается со старым значением.
