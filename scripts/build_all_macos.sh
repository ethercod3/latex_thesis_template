#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_DIR=$(dirname "$SCRIPT_DIR")

cd "$PROJECT_DIR"

run_profile() {
    profile="$1"
    service="$2"

    printf '\n==> %s\n' "$profile"
    docker compose --profile "$profile" run --rm --build "$service"
}

run_profile docx docx_pdf
run_profile mermaid mermaid_diagrams
run_profile python python_diagrams
run_profile latex latex
