# Task files

| Файл | Комманды |
| --- | --- |
| `build.yml` | `build` |
| `docker.yml` | `build:images`, `build:image`, `compose:up`, `compose:down` |
| `docs.yml` | `docs`, `docs:build`, `docs:build:pages`, `docs:pull`, `docs:down` |
| `latex.yml` | `latex:local`, `latex:manual_chain`, `latex:docker` |
| `diagrams.yml` | `mermaid`, `mermaid:docker`, `diagrams`, `diagrams:docker` |
| `docx.yml` | `docx`, `docx:keep-blank` |
| `tools.yml` | `deps`, `hooks`, `clean`, `clean:dry`, `hash`, `diff` |

Запустите `task --list` из корня проекта чтобы увидеть полный список задач.
