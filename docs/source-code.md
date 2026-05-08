# Код в приложениях

## Если кода нет

Если файлов кода нет и нужно скомпилировать проект без них, закомментируйте эти строки в конце `.tex` файла:

```latex
\newpage
\input{appendix_b.tex}
\newpage
\input{include_listings.tex}
```

В LaTeX комментарий начинается с `%`.

## Если код есть

Положите код на одном уровне с папкой LaTeX-кода. При компиляции LaTeX обращается к файлам по такому пути:

```text
../vault_diploma/<файл>
```

При Docker-сборке путь к коду задается через `.env`:

```env
VAULT_PATH="/vault_code"
VAULT_OS_PATH="../vault_diploma"
```

`VAULT_OS_PATH` - путь на вашей машине, `VAULT_PATH` - путь внутри контейнера.
