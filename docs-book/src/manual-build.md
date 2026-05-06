# Ручная сборка

## Через скрипт

1. Установите дистрибутив LaTeX. Под Windows рекомендуется TeX Live. Компилятор проекта: LuaLaTeX.
2. Клонируйте репозиторий.
3. Установите Python-зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте в корне проекта файл `.env` и укажите основной `.tex` файл:

```env
TARGET="Куприянов_И221_диплом.tex"
```

5. Запустите ручную сборку:

```bash
python scripts/build_latex_manual.py
```

Скрипт читает `TARGET` из `.env`, создает `.aux_files`, запускает `lualatex`, затем `biber`, затем еще два раза `lualatex`. Итоговый PDF копируется из `.aux_files` в корень проекта.

Если нужно собрать другой файл без изменения `.env`, передайте его явно:

```bash
python scripts/build_latex_manual.py --target "<файл>.tex"
```

## Без скрипта

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
