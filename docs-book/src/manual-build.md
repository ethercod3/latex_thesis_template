# Сборка без Docker

Рекомендуемый способ сборки LaTeX-документа без Docker - `latexmk`. Он сам запускает `lualatex` и `biber` нужное количество раз по правилам из `.latexmkrc`.

> **Важно:** в этом проекте `latexmk` заметно сокращает время компиляции. Типичный запуск через `latexmk` занимает около 18 секунд, а режим `--no-latexmk` с ручной цепочкой - около 53 секунд.

## Подготовка

1. Установите дистрибутив LaTeX. Под Windows рекомендуется TeX Live. `latexmk` обычно поставляется вместе с установкой TeX Live, поэтому отдельно его ставить не нужно. Компилятор проекта: LuaLaTeX.
2. Убедитесь, что доступны команды `latexmk`, `lualatex` и `biber`.
3. Клонируйте репозиторий.
4. Установите Python-зависимости для вспомогательных скриптов:

```bash
pip install -r requirements.txt
```

5. Создайте в корне проекта файл `.env` и укажите основной `.tex` файл:

```env
TARGET="Куприянов_И221_диплом.tex"
```

## Сборка через latexmk

Соберите основной документ:

```bash
latexmk "Куприянов_И221_диплом.tex"
```

Для другого `.tex` файла:

```bash
latexmk "<файл>.tex"
```

Конфигурация находится в `.latexmkrc`: используется `LuaLaTeX`, `biber`, вспомогательные файлы складываются в `.aux_files`, а готовый PDF остается в корне проекта.

## Сборка через Python-скрипт

Если удобнее читать `TARGET` из `.env`, можно использовать скрипт. По умолчанию он тоже собирает документ через `latexmk`:

```bash
python scripts/build_latex_manual.py
```

Если нужно собрать другой файл без изменения `.env`, передайте его явно:

```bash
python scripts/build_latex_manual.py --target "<файл>.tex"
```

Если нужно отключить `latexmk` и запустить старую ручную цепочку `lualatex`, `biber`, `lualatex`, `lualatex`, передайте флаг:

```bash
python scripts/build_latex_manual.py --no-latexmk
```

Этот режим медленнее: в текущем проекте около 53 секунд против примерно 18 секунд через `latexmk`.

## Полностью ручная компиляция

Этот способ нужен только для диагностики или если `latexmk` недоступен. В обычной сборке без Docker используйте `latexmk`: в этом проекте он сокращает время компиляции примерно с 53 до 18 секунд. В скрипте `scripts/build_latex_manual.py` этот режим включается флагом `--no-latexmk`.

Создайте папку для вспомогательных файлов:

```bash
mkdir .aux_files
```

Так как проект использует `biblatex` с backend `biber`, одного запуска `lualatex` недостаточно:

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
