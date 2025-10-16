#!/usr/bin/env bash

# follow symlink to get actual script location
SCRIPT_PATH="${BASH_SOURCE[0]}"

while [ -L "$SCRIPT_PATH" ]; do
    SCRIPT_DIR="$(cd -P "$(dirname "$SCRIPT_PATH")" &> /dev/null && pwd)"
    SCRIPT_PATH="$(readlink "$SCRIPT_PATH")"
    [[ $SCRIPT_PATH != /* ]] && SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_PATH"
done

SCRIPT_DIR="$(cd -P "$(dirname "$SCRIPT_PATH")" &> /dev/null && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$HOME/.local/share/BakkesLinux"
RUNNER_PATH="$HOME/.local/bin/bakkesmod"

log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

log_success() {
    echo "[SUCCESS] $1"
}

cmd_run() {
    log_info "Running BakkesMod"
    bash "$REPO_DIR/run.sh" "$@"
}

cmd_update() {
    log_info "Updating BakkesLinux repository..."

    if [ ! -d "$REPO_DIR/.git" ]; then
        log_error "Repository not found at $REPO_DIR"
        log_error "This doesn't look like a git repository"
        exit 1
    fi

    cd "$REPO_DIR"
    git pull
    log_success "Repository updated successfully"
}

cmd_remove() {
    log_info "Removing BakkesLinux installation..."

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

            log_success "BakkesLinux removed successfully"
            log_info "Repository at $REPO_DIR was not removed"
            ;;
        * )
            log_info "cancelled"
            ;;
    esac
}

show_usage() {
    echo "Usage: bakkesmod <command> [options]"
    echo ""
    echo "Commands:"
    echo "  run     [--standalone --platform] Run BakkesMod"
    echo "  install [--platform]              Install BakkesMod on the specified prefix"
    echo "  update                            Update BakkesLinux repository"
    echo "  remove                            Remove BakkesLinux installation"
    echo "  help                              Show this help message"
}

case "$1" in
    run)
        shift
        cmd_run "$@"
        ;;
    update)
        cmd_update
        ;;
    remove)
        cmd_remove
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        if [ -z "$1" ]; then
            cmd_run
        else
            log_error "Unknown command: $1"
            show_usage
            exit 1
        fi
        ;;
esac
