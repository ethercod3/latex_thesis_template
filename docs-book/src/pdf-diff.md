# Сравнение PDF между коммитами

![Пример визуального сравнения PDF](assets/pdf_diff_example.png)

Если нужно посмотреть визуальную разницу между двумя версиями диплома, используйте скрипт:

{{#tabs global="runmode"}}

{{#tab name="Task"}}

```bash
task diff -- <commit_1> <commit_2>
```

{{#endtab}}

{{#tab name="Ручной"}}

```bash
python scripts/diff_pdf_commits.py <commit_1> <commit_2>
```

{{#endtab}}

{{#endtabs}}

Скрипт принимает два хэша коммита, по очереди переключается на каждый из них, собирает PDF через Docker, складывает две версии во временную папку и открывает `diff-pdf`.

Результат можно только открыть, только сохранить или сделать оба действия:

{{#tabs global="runmode"}}

{{#tab name="Task"}}

```bash
task diff -- <commit_1> <commit_2> --view
task diff -- <commit_1> <commit_2> --save
task diff -- <commit_1> <commit_2> --view --save
task diff -- <commit_1> <commit_2> --save path/to/diff.pdf
```

{{#endtab}}

{{#tab name="Ручной"}}

```bash
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --view
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --save
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --view --save
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --save path/to/diff.pdf
```

{{#endtab}}

{{#endtabs}}

Без `--view` и `--save` скрипт открывает diff. При `--save` без пути результат сохраняется в `.pdf_diff/saved`.

Скачать `diff-pdf` можно в репозитории: <https://github.com/vslavik/diff-pdf/>

## Профили сборки

По умолчанию запускаются все профили в порядке: `docx` \\(\\rightarrow\\) `mermaid` \\(\\rightarrow\\) `python` \\(\\rightarrow\\) `latex`.

Если нужно ограничить сборку, передайте опцию `--profiles`:

{{#tabs global="runmode"}}

{{#tab name="Task"}}

```bash
task diff -- <commit_1> <commit_2> --profiles all
task diff -- <commit_1> <commit_2> --profiles docx
task diff -- <commit_1> <commit_2> --profiles mermaid
task diff -- <commit_1> <commit_2> --profiles python
task diff -- <commit_1> <commit_2> --profiles mermaid,python
task diff -- <commit_1> <commit_2> --profiles latex
```

{{#endtab}}

{{#tab name="Ручной"}}

```bash
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles all
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles docx
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles mermaid
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles python
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles mermaid,python
python scripts/diff_pdf_commits.py <commit_1> <commit_2> --profiles latex
```

{{#endtab}}

{{#endtabs}}

Значения:

| Значение | Что запускается |
| --- | --- |
| `all` | `docx` \\(\\rightarrow\\) `mermaid` \\(\\rightarrow\\) `python` \\(\\rightarrow\\) `latex` |
| `docx` | `docx` \\(\\rightarrow\\) `latex` |
| `mermaid` | `mermaid` \\(\\rightarrow\\) `latex` |
| `python` | `python` \\(\\rightarrow\\) `latex` |
| `latex` | Только `latex` |
| `mermaid,python` | `mermaid` \\(\\rightarrow\\) `python` \\(\\rightarrow\\) `latex` |

В `--profiles` можно передать несколько профилей через запятую: `docx,python`, `mermaid,python`, `docx,mermaid,python`. Скрипт запускает их в порядке `docx` \\(\\rightarrow\\) `mermaid` \\(\\rightarrow\\) `python` \\(\\rightarrow\\) `latex`.

Если `latex` не указан явно, он добавляется автоматически, потому что именно этот профиль собирает итоговый PDF для сравнения.

Перед запуском рабочее дерево Git должно быть чистым. После завершения скрипт возвращается на исходный `HEAD`, удаляет временные файлы и восстанавливает текущие файлы из `figures`, а также PDF в корне проекта, например `титульник.pdf` и `задание.pdf`.
