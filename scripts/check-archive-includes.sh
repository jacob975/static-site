#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: scripts/check-archive-includes.sh [--recursive]

Checks archive HTML pages for:
1) mathjax-fixes.css include
2) shared-post-widgets.js include (assets/js)
3) Google Analytics snippet (gtag loader + gtag config)

Options:
  --recursive   Check all HTML files under archives/** (includes category pages)
  -h, --help    Show this help message
EOF
}

recursive=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --recursive)
            recursive=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            exit 2
            ;;
    esac
done

if [[ ! -d "archives" ]]; then
    echo "Error: run this script from repository root (archives directory not found)." >&2
    exit 2
fi

# Build target file list.
declare -a files=()
if [[ "$recursive" == true ]]; then
    while IFS= read -r file; do
        files+=("$file")
    done < <(find archives -type f -name "*.html" | sort)
else
    while IFS= read -r file; do
        files+=("$file")
    done < <(find archives -maxdepth 1 -type f -name "*.html" | sort)
fi

if [[ ${#files[@]} -eq 0 ]]; then
    echo "No HTML files found in target scope."
    exit 0
fi

declare -a missing_mathjax=()
declare -a missing_widgets=()
declare -a typo_asserts_widgets=()
declare -a missing_ga=()

for file in "${files[@]}"; do
    if ! rg -q "mathjax-fixes\\.css" "$file"; then
        missing_mathjax+=("$file")
    fi

    has_widgets_assets=false
    has_widgets_asserts=false
    if rg -q "assets/js/shared-post-widgets\\.js" "$file"; then
        has_widgets_assets=true
    fi
    if rg -q "asserts/js/shared-post-widgets\\.js" "$file"; then
        has_widgets_asserts=true
    fi

    if [[ "$has_widgets_assets" == false ]]; then
        missing_widgets+=("$file")
    fi
    if [[ "$has_widgets_asserts" == true ]]; then
        typo_asserts_widgets+=("$file")
    fi

    has_ga_loader=false
    has_ga_config=false
    if rg -q "googletagmanager\\.com/gtag/js\\?id=|id=\"google_gtagjs-js\"" "$file"; then
        has_ga_loader=true
    fi
    if rg -q 'gtag\("config"' "$file"; then
        has_ga_config=true
    fi
    if [[ "$has_ga_loader" == false || "$has_ga_config" == false ]]; then
        missing_ga+=("$file")
    fi
done

print_list() {
    local title="$1"
    shift
    local -a arr=("$@")
    echo
    echo "$title (${#arr[@]}):"
    for f in "${arr[@]}"; do
        echo "  - $f"
    done
}

echo "Checked files: ${#files[@]}"

action_required=false

if [[ ${#missing_mathjax[@]} -gt 0 ]]; then
    print_list "Missing mathjax-fixes.css" "${missing_mathjax[@]}"
    action_required=true
fi

if [[ ${#missing_widgets[@]} -gt 0 ]]; then
    print_list "Missing assets/js/shared-post-widgets.js" "${missing_widgets[@]}"
    action_required=true
fi

if [[ ${#missing_ga[@]} -gt 0 ]]; then
    print_list "Missing Google Analytics snippet" "${missing_ga[@]}"
    action_required=true
fi

if [[ ${#typo_asserts_widgets[@]} -gt 0 ]]; then
    print_list "Found typo path asserts/js/shared-post-widgets.js" "${typo_asserts_widgets[@]}"
    action_required=true
fi

if [[ "$action_required" == true ]]; then
    echo
    echo "Result: FAILED"
    exit 1
fi

echo "Result: OK"
