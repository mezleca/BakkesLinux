#!/usr/bin/env python3

import os
import sys
import time
import requests
import zipfile
from pathlib import Path
from typing import Optional
from utils import (
    get_proton_path,
    log_info,
    log_error,
    log_success,
    check_required_commands,
    run_command,
    is_process_running,
    ensure_dir,
    get_home_dir,
)
from config import set_launch_options

HOME = get_home_dir()
REPO_DIR = str(Path(__file__).parent.parent.absolute())
CONFIG_DIR = f"{HOME}/.local/share/BakkesLinux"
BIN_DIR = f"{HOME}/.local/bin"
DESKTOP_DIR = f"{HOME}/.local/share/applications"
RUNNER_PATH = f"{BIN_DIR}/bakkesmod"
CONFIG_FILE = f"{CONFIG_DIR}/repo_path"
DOWNLOAD_URL = "https://github.com/bakkesmodorg/BakkesModInjectorCpp/releases/latest/download/BakkesModSetup.zip"
REQUIRED_COMMANDS = ["mkdir", "rm", "curl", "killall", "sleep"]


def save_repo_path() -> bool:
    ensure_dir(CONFIG_DIR)

    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(REPO_DIR)
        log_success(f"Saved repository path: {REPO_DIR}")
        return True
    except Exception as e:
        log_error(f"Failed to save repo path: {e}")
        return False


def download_bakkesmod_setup() -> Optional[str]:
    zip_path = f"{REPO_DIR}/BakkesModSetup.zip"
    extract_dir = f"{REPO_DIR}/BakkesModSetup"

    log_info(f"Downloading BakkesModSetup.zip from {DOWNLOAD_URL}")

    try:
        response = requests.get(DOWNLOAD_URL, stream=True)
        response.raise_for_status()

        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        log_success("Download complete")

        ensure_dir(extract_dir)

        log_info("Extracting BakkesModSetup.zip")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        os.remove(zip_path)
        log_success("BakkesModSetup extracted successfully")

        return extract_dir

    except Exception as e:
        log_error(f"Failed to download/extract BakkesModSetup: {e}")
        return None


def wait_process_exit(process_name: str, message: str) -> None:
    log_info(message)
    log_info(f"You have to manually close {process_name}")

    while is_process_running(process_name):
        time.sleep(1)


def setup_prefix_and_install(setup_exe_path: str) -> bool:
    wait_process_exit("RocketLeague.exe", "Waiting for RocketLeague to exit")

    proton_path = get_proton_path("")
    if not proton_path:
        return False

    rl_prefix = f"{HOME}/.steam/steam/steamapps/compatdata/252950"
    wine_prefix = f"{rl_prefix}/pfx"
    wine_bin = f"{proton_path}/bin/wine64"

    log_info("Configuring prefix to Windows 10")

    wine_cmd = f'WINEFSYNC=1 WINEPREFIX="{wine_prefix}" "{wine_bin}" winecfg /v win10'
    _ = run_command(wine_cmd, True, True)

    log_info("Running BakkesMod setup executable")

    setup_exe = Path(setup_exe_path, "BakkesModSetup.exe")
    os.chmod(setup_exe, 0o755)

    install_cmd = f'WINEFSYNC=1 WINEPREFIX="{wine_prefix}" "{wine_bin}" "{setup_exe}"'
    if not run_command(install_cmd):
        log_error("Failed to run BakkesMod setup")
        return False

    return True


def create_bakkesmod_symlink() -> bool:
    log_info(f"Creating bakkesmod symlink at {RUNNER_PATH}")

    runner_script = f"{REPO_DIR}/src/runner.sh"

    if not Path(runner_script).exists():
        log_error(f"runner.sh not found: {runner_script}")
        return False

    try:
        runner_path = Path(RUNNER_PATH)

        # remove old symlink/file if exists
        if runner_path.exists() or runner_path.is_symlink():
            runner_path.unlink()

        os.symlink(runner_script, RUNNER_PATH)

        # ensure exec permission
        os.chmod(RUNNER_PATH, 0o755)
        log_success("Symlink created successfully")
        return True
    except Exception as e:
        log_error(f"Failed to create symlink: {e}")
        return False


def create_desktop_file() -> bool:
    log_info(f"Creating desktop file at {DESKTOP_DIR}/bakkesmod.desktop")

    desktop_content = f"""[Desktop Entry]
Name=BakkesMod
Comment=Bakkesmod for Rocket League (STEAM)
Exec={RUNNER_PATH} run --standalone
Icon=applications-games
Terminal=false
Type=Application
Categories=Game;
"""

    try:
        desktop_path = f"{DESKTOP_DIR}/bakkesmod.desktop"
        with open(desktop_path, "w") as f:
            f.write(desktop_content)

        os.chmod(desktop_path, 0o644)
        log_success("Desktop file created successfully")
        return True
    except Exception as e:
        log_error(f"Failed to create desktop file: {e}")
        return False


def setup_launch_options() -> None:
    response = input(
        "Do you want to set launch options for RocketLeague? (y/n) "
    ).lower()

    if response == "y":
        wait_process_exit("steam", "Waiting for Steam to exit")

        run_script = f"{REPO_DIR}/run.sh"
        if set_launch_options(run_script):
            log_success("Launch options set successfully")
        else:
            log_error("Failed to set launch options")
    elif response == "n":
        log_info("Skipping launch options setup")
    else:
        log_error("Invalid response")


def install() -> int:
    os.environ["WINEDEBUG"] = "-all"

    if not check_required_commands(REQUIRED_COMMANDS):
        return 1

    log_info("Creating directories...")
    ensure_dir(CONFIG_DIR)
    ensure_dir(BIN_DIR)
    ensure_dir(DESKTOP_DIR)

    if not save_repo_path():
        return 1

    setup_dir = download_bakkesmod_setup()
    if not setup_dir:
        return 1

    if not setup_prefix_and_install(setup_dir):
        return 1

    if not create_bakkesmod_symlink():
        return 1

    if not create_desktop_file():
        return 1

    setup_launch_options()

    log_success("Installation complete!")
    log_info("You can now run 'bakkesmod' from anywhere")

    return 0


if __name__ == "__main__":
    sys.exit(install())
