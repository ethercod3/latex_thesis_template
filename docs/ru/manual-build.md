# Сборка без Docker

Рекомендуемый способ сборки LaTeX-документа без Docker - `latexmk`. Он сам запускает `lualatex` и `biber` нужное количество раз по правилам из `.latexmkrc`.

!!! warning "Важно"
    В этом проекте `latexmk` заметно сокращает время повторной компиляции. Первый запуск через `latexmk` занимает около 74 секунд, повторный - около 18 секунд. Режим `--no-latexmk` с ручной цепочкой каждый раз занимает примерно 53-54 секунды.

Первый запуск `latexmk` может быть дольше ручной сборки, потому что он строит свое служебное состояние, анализирует зависимости, создает `.fdb_latexmk` и выполняет полный цикл сборки.[^latexmk-cache] На следующих запусках `latexmk` использует эту информацию и пересобирает только то, что действительно изменилось.

## Что нужно подготовить отдельно

!!! warning "Внешние артефакты"
    `latexmk` собирает только LaTeX-документ. Перед сборкой без Docker нужно отдельно подготовить все внешние артефакты, которые подключаются в `.tex`:

    - `титульник.pdf` и `задание.pdf` должны лежать в корне проекта. Их можно получить из `docx/*.docx` вручную через Microsoft Word или LibreOffice, см. [Титульники](/title-pages/).
    - Mermaid-диаграммы из `mermaid/*.mmd` нужно заранее сгенерировать в `figures/`, см. [Диаграммы](/diagrams/).
    - Python-диаграммы нужно заранее сгенерировать командой `task diagrams` или вручную `python scripts/compile_python_diagrams.py`.
    - Если в приложениях подключается код, он должен лежать по ожидаемому пути, см. [Код в приложениях](/source-code/).

    Если эти файлы не подготовлены, `latexmk` может завершиться ошибкой из-за отсутствующих PDF, изображений или листингов.

## Подготовка

1. Установите дистрибутив LaTeX. Под Windows рекомендуется TeX Live. `latexmk` обычно поставляется вместе с установкой TeX Live, поэтому отдельно его ставить не нужно. Компилятор проекта: LuaLaTeX.
2. Установите Python и убедитесь, что команда `python` доступна в `PATH`. Она нужна не только вспомогательным скриптам: документ использует PyLuaTeX во время компиляции LaTeX.
3. Убедитесь, что доступны команды `latexmk`, `lualatex` и `biber`.
4. Клонируйте репозиторий.
5. Установите Python-зависимости для вспомогательных скриптов:



=== "Task"


    ```bash
    task deps
    ```



=== "Ручной"


    ```bash
    pip install -r requirements.txt
    ```





6. Создайте в корне проекта файл `.env` и укажите основной `.tex` файл:

```env
TARGET="Куприянов_И221_диплом.tex"
```

## Сборка через latexmk

Соберите основной документ:



=== "Task"


    ```bash
    task latex:local
    ```



=== "Ручной"


    ```bash
    latexmk "Куприянов_И221_диплом.tex"
    ```





Для другого `.tex` файла:



=== "Task"


    ```bash
    task latex:local -- --target "<файл>.tex"
    ```



=== "Ручной"


    ```bash
    latexmk "<файл>.tex"
    ```





Конфигурация находится в `.latexmkrc`: используется `LuaLaTeX` с `--shell-escape`, `biber`, вспомогательные файлы складываются в `.aux_files`, а готовый PDF остается в корне проекта. `--shell-escape` нужен PyLuaTeX, чтобы запустить Python во время компиляции.

## Сборка через Python-скрипт

Если удобнее читать `TARGET` из `.env`, можно использовать скрипт. По умолчанию он тоже собирает документ через `latexmk`:



=== "Task"


    ```bash
    task latex:local
    ```



=== "Ручной"


    ```bash
    python scripts/build_latex_manual.py
    ```





Если нужно собрать другой файл без изменения `.env`, передайте его явно:



=== "Task"


    ```bash
    task latex:local -- --target "<файл>.tex"
    ```



=== "Ручной"


    ```bash
    python scripts/build_latex_manual.py --target "<файл>.tex"
    ```





Если нужно отключить `latexmk` и запустить старую ручную цепочку `lualatex`, `biber`, `lualatex`, `lualatex`, передайте флаг:



=== "Task"


    ```bash
    task latex:manual_chain
    ```



=== "Ручной"


    ```bash
    python scripts/build_latex_manual.py --no-latexmk
    ```





!!! note "Когда нужен ручной режим"
    Этот режим медленнее на повторных сборках: в текущем проекте около 53-54 секунд каждый раз против примерно 18 секунд при повторном запуске через `latexmk`.

## Полностью ручная компиляция

Этот способ нужен только для диагностики или если `latexmk` недоступен. В обычной сборке без Docker используйте `latexmk`: первый запуск в этом проекте может занимать около 74 секунд, зато повторные сборки сокращаются примерно до 18 секунд. Ручная цепочка через `--no-latexmk` каждый раз занимает около 53-54 секунд. В скрипте `scripts/build_latex_manual.py` этот режим включается флагом `--no-latexmk`.

Создайте папку для вспомогательных файлов:

```bash
mkdir .aux_files
```

Так как проект использует `biblatex` с backend `biber` и PyLuaTeX, одного запуска `lualatex` недостаточно, а каждый запуск `lualatex` должен идти с `--shell-escape`:

??? example "Ручная цепочка для произвольного `.tex` файла"
    ```bash
    lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "<файл>.tex"
    biber ".aux_files/<файл>.bcf"
    lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "<файл>.tex"
    lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "<файл>.tex"
    ```

Для основного файла проекта:

??? example "Ручная цепочка для основного файла проекта"
    ```bash
    lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "Куприянов_И221_диплом.tex"
    biber ".aux_files/Куприянов_И221_диплом.bcf"
    lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "Куприянов_И221_диплом.tex"
    lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "Куприянов_И221_диплом.tex"
    ```

После сборки итоговый PDF окажется в `.aux_files`. Его нужно перенести в корень проекта:

```bash
mv ".aux_files/<файл>.pdf" .
```

В Windows `cmd` для основного файла:

```bat
move ".aux_files\Куприянов_И221_диплом.pdf" .
```

[^latexmk-cache]: Служебные файлы `latexmk` помогают понять, какие зависимости документа изменились: библиография, подключенные `.tex`-файлы, изображения и вспомогательные LaTeX-артефакты. Поэтому повторная сборка обычно короче полной ручной цепочки.
