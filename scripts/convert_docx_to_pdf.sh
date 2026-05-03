#!/bin/sh
set -eu

INPUT_DIR="${DOCX_INPUT_DIR:-/data/docx}"
OUTPUT_DIR="${PDF_OUTPUT_DIR:-/data}"
TMP_DIR="$(mktemp -d)"
PDF_EXPORT_FILTER='pdf:writer_pdf_Export:{"IsSkipEmptyPages":{"type":"boolean","value":"true"}}'
SKIP_BLANK_PAGES="${SKIP_BLANK_PAGES:-1}"

cleanup() {
    rm -rf "$TMP_DIR"
}

trap cleanup EXIT INT TERM

remove_blank_pages() {
    input_file="$1"
    output_file="$2"
    bbox_file="$TMP_DIR/$(basename "$input_file" .pdf).bbox"
    keep_pages_file="$TMP_DIR/$(basename "$input_file" .pdf).pages"

    : > "$keep_pages_file"

    gs -q -dNOPAUSE -dBATCH -sDEVICE=bbox "$input_file" > /dev/null 2> "$bbox_file"

    page=0
    kept=0

    while IFS= read -r line; do
        case "$line" in
            "%%BoundingBox:"*)
                page=$((page + 1))
                set -- $line

                if [ "${2:-0}" = "0" ] && [ "${3:-0}" = "0" ] && [ "${4:-0}" = "0" ] && [ "${5:-0}" = "0" ]; then
                    echo "Skipping blank page $page in $input_file"
                else
                    printf '%s\n' "$page" >> "$keep_pages_file"
                    kept=$((kept + 1))
                fi
                ;;
        esac
    done < "$bbox_file"

    if [ "$page" -eq 0 ] || [ "$kept" -eq "$page" ]; then
        cp "$input_file" "$output_file"
        return
    fi

    if [ "$kept" -eq 0 ]; then
        echo "All pages look blank in $input_file; keeping original PDF" >&2
        cp "$input_file" "$output_file"
        return
    fi

    pages="$(tr '\n' ' ' < "$keep_pages_file")"
    qpdf --empty --pages "$input_file" $pages -- "$output_file"
}

if [ ! -d "$INPUT_DIR" ]; then
    echo "Input directory not found: $INPUT_DIR" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

found=0

for source_file in "$INPUT_DIR"/*.docx; do
    [ -e "$source_file" ] || continue

    found=1
    base_name="$(basename "$source_file" .docx)"
    output_file="$OUTPUT_DIR/$base_name.pdf"
    converted_file="$TMP_DIR/$base_name.pdf"

    echo "Converting $source_file -> $output_file"
    soffice \
        --headless \
        --nologo \
        --nofirststartwizard \
        --nodefault \
        --nolockcheck \
        --convert-to "$PDF_EXPORT_FILTER" \
        --outdir "$TMP_DIR" \
        "$source_file"

    if [ ! -f "$converted_file" ]; then
        echo "LibreOffice did not produce expected file: $converted_file" >&2
        exit 1
    fi

    if [ "$SKIP_BLANK_PAGES" = "1" ]; then
        remove_blank_pages "$converted_file" "$output_file"
    else
        cp "$converted_file" "$output_file"
    fi

    rm -f "$converted_file"
done

if [ "$found" -eq 0 ]; then
    echo "No .docx files found in $INPUT_DIR" >&2
    exit 1
fi
