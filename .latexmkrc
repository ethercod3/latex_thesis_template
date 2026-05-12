# Конфигурация latexmk для сборки диплома.
#
# Документ собирается через LuaLaTeX с включенным shell-escape: это нужно
# для пакетов и инструментов, которые создают вспомогательные артефакты во
# время компиляции. Все временные файлы складываются в .aux_files, чтобы
# корень проекта оставался чистым, а итоговый PDF появлялся рядом с .tex.
# Biber используется как движок библиографии.

$pdf_mode = 4;
$aux_dir = '.aux_files';
$out_dir = ".";
$lualatex = "lualatex --shell-escape -synctex=1 -interaction=nonstopmode %O %S";
$biber = "biber %O %S";
