=pod

Конфигурация latexmk для сборки диплома.

Документ собирается через LuaLaTeX с включенным shell-escape: это нужно
для пакетов и инструментов, которые создают вспомогательные артефакты во
время компиляции. Все временные файлы складываются в .aux_files, чтобы
корень проекта оставался чистым, а итоговый PDF появлялся рядом с .tex.
Biber используется как движок библиографии.

Полезные ссылки:
    - latexmk на CTAN: https://ctan.org/pkg/latexmk
    - домашняя страница latexmk: https://www.cantab.net/users/johncollins/latexmk/
    - документация LuaTeX: https://www.luatex.org/documentation.html
    - Biber на CTAN: https://ctan.org/pkg/biber
    - репозиторий Biber: https://github.com/plk/biber
    - репозиторий biblatex: https://github.com/plk/biblatex

=cut

$pdf_mode = 4;
$aux_dir = '.aux_files';
$out_dir = ".";
$lualatex = "lualatex --shell-escape -synctex=1 -interaction=nonstopmode %O %S";
$biber = "biber %O %S";
