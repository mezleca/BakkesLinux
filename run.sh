#!/usr/bin/env bash

SCRIPT_PATH="${BASH_SOURCE[0]}"

# follow symlink to get actual script location
while [ -L "$SCRIPT_PATH" ]; do
    SCRIPT_DIR="$(cd -P "$(dirname "$SCRIPT_PATH")" &> /dev/null && pwd)"
    SCRIPT_PATH="$(readlink "$SCRIPT_PATH")"
    [[ $SCRIPT_PATH != /* ]] && SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_PATH"
done

SCRIPT_DIR="$(cd -P "$(dirname "$SCRIPT_PATH")" &> /dev/null && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_CMD="python3"
CONFIG_DIR="$HOME/.local/share/BakkesLinux"
RUNNER_PATH="$HOME/.local/bin/bakkesmod"

log_info() {
    echo "[LOG] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

show_usage() {
    echo "Usage: ./run.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  run     [--standalone --platform] Run BakkesMod"
    echo "  install [--platform]              Install BakkesMod on the specified prefix"
    echo "  update                            Update BakkesLinux repository"
    echo "  remove                            Remove BakkesLinux installation"
    echo "  help                              Show this help message"
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
fi

# activate venv and run appropriate script
source "$VENV_DIR/bin/activate"

# always install dependencies
"$VENV_DIR/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"

case "$1" in
    run|"")
        if [ "$1" = "run" ]; then
            shift
        fi
        python "$SCRIPT_DIR/src/bakkes.py" "$@"
        ;;
    install)
        shift
        python "$SCRIPT_DIR/src/installer.py" "$@"
        ;;
    update)
        log_info "Updating BakkesLinux repository..."
        if [ ! -d "$SCRIPT_DIR/.git" ]; then
            log_error "Repository not found at $SCRIPT_DIR"
            log_error "This doesn't look like a git repository"
            deactivate
            exit 1
        fi
        cd "$SCRIPT_DIR" || exit 1
        git pull
        log_info "Repository updated successfully"
        ;;
    remove)
        read -p "Are you sure you want to remove BakkesLinux? (y/n) " confirm
        case "$confirm" in
            y|Y )
                log_info "Removing config directory..."
                rm -rf "$CONFIG_DIR"
                log_info "Removing desktop files..."
                rm -f "$HOME/.local/share/applications/bakkesmod-steam.desktop"
                rm -f "$HOME/.local/share/applications/bakkesmod-heroic.desktop"
                rm -f "$HOME/.local/share/applications/bakkesmod.desktop"
                log_info "Removing runner..."
                rm -f "$RUNNER_PATH"
                log_info "BakkesLinux removed successfully (repository at $SCRIPT_DIR not removed)"
                ;;
            * )
                log_info "cancelled"
                ;;
        esac
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        log_error "Unknown command: $1"
        show_usage
        deactivate
        exit 1
        ;;
esac

deactivate
