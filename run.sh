#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_CMD="python3"

log_info() {
    echo "[LOG] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

# check if python is available
if ! command -v "$PYTHON_CMD" &> /dev/null; then
    log_error "python3 is not installed!"
    exit 1
fi

# check/create venv
if [ ! -d "$VENV_DIR" ]; then
    log_info "creating python env..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"

    if [ $? -ne 0 ]; then
        log_error "failed to create env"
        exit 1
    fi

    if [ $? -ne 0 ]; then
        log_error "failed to install dependencies"
        exit 1
    fi
fi

# activate venv and run appropriate script
source "$VENV_DIR/bin/activate"

# always install dependencies
"$VENV_DIR/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"

case "$1" in
    install)
        python "$SCRIPT_DIR/src/installer.py" "${@:2}"
        ;;
    *)
        python "$SCRIPT_DIR/src/bakkes.py" "$@"
        ;;
esac

deactivate
