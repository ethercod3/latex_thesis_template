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

Положите код на одном уровне с папкой LaTeX-кода.[^vault-path]

При Docker-сборке путь к коду задается через `.env`:

```env
VAULT_PATH="/vault_code"
VAULT_OS_PATH="../vault_diploma"
```

`VAULT_OS_PATH` - путь на вашей машине, `VAULT_PATH` :material-information-outline:{ title="Путь внутри Linux-контейнера, куда Docker монтирует каталог с кодом." } - путь внутри контейнера.

[^vault-path]: При локальной компиляции LaTeX обращается к файлам по пути `../vault_diploma/<файл>`. В Docker-сборке `VAULT_OS_PATH` указывает на этот каталог на вашей машине, а `VAULT_PATH` задает путь, по которому тот же каталог будет виден внутри Linux-контейнера.
