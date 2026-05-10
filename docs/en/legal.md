# Legal information

This page records the legal status of materials stored in the repository or used when building the documentation and PDF. It does not replace license texts and is not legal advice.

## Project license

The repository root contains `LICENSE.md`. It uses a mixed licensing model:

| Materials | License |
| --- | --- |
| Code, scripts, Docker/Task configuration, and helper automation | PolyForm Noncommercial License 1.0.0 |
| Documentation, authored text, LaTeX sources, diagrams, and explanatory materials | Creative Commons Attribution-NonCommercial 4.0 International |
| Fonts in `fonts/latin-modern-mono/` | GUST Font License from `fonts/latin-modern-mono/GUST-FONT-LICENSE.TXT` |

Noncommercial use is allowed under the corresponding license terms. Commercial use is not granted automatically and requires a separate written agreement with the author.

Commercial use can include, for example, inclusion in a paid product, paid course, commercial consulting deliverable, closed corporate documentation, or service.

## Fonts

The `fonts/latin-modern-mono/` directory contains Latin Modern Mono files:

- `*.otf` - font files;
- `GUST-FONT-LICENSE.TXT` - license text;
- `lm-info.pdf` - reference information about the Latin Modern family.

According to `fonts/latin-modern-mono/GUST-FONT-LICENSE.TXT`, these fonts are distributed under the GUST Font License version 1.0, dated June 22, 2009. The license permits distribution and modification of the work under the LaTeX Project Public License version 1.3c or any later version.

For derived font versions, the license requests, but does not legally require, changing the names of the fonts and files that make up the derived work. The full and binding terms are in the license file itself: `fonts/latin-modern-mono/GUST-FONT-LICENSE.TXT`.

The `LICENSE.md` file does not change the license of these fonts and does not grant additional rights to them.

## Third-party tools

The repository contains configuration and instructions for third-party tools, but those tools are distributed under their own licenses:

| Tool | Where it is used |
| --- | --- |
| Docker and Docker Compose | reproducible profile builds |
| TeX Live, LuaLaTeX, latexmk, biber | LaTeX document build |
| Zensical | documentation build |
| Mermaid CLI | Mermaid diagram generation |
| Python libraries from `requirements.txt` | helper scripts and diagrams |
| diff-pdf | visual PDF comparison |

Before distributing built artifacts or Docker images, take the licenses of these dependencies and images into account.

## Images and documents

Images in `docs/ru/assets/`, `.github/images/`, `figures/`, and PDF/DOCX files can contain derivative materials: UI screenshots, exported diagrams, title pages, the assignment, and fragments of the final diploma. Their legal status can differ from the source code status.

Before public publication, it is worth checking that:

- screenshots do not contain personal data or internal information;
- title pages and the assignment can be distributed under the rules of the educational institution;
- PDFs do not contain local paths, user names, or private data;
- publication complies with diploma work requirements.

## Local paths and private data

The `.env` file is not committed and is intended for local paths such as `VAULT_OS_PATH`. Do not add private keys, tokens, absolute paths to personal directories, or closed source code to the repository unless you have permission to do so.

## Disclaimer

This page describes the current state of the repository and helps keep important legal details visible before publication. For a formal license choice or rights review, rely on primary license texts and, when necessary, a qualified specialist.
