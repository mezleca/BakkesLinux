#!/usr/bin/env python3

import os
import sys
import time
import requests
import zipfile
import argparse
from pathlib import Path
from utils import (
    CONFIG_DIR,
    DESKTOP_DIR,
    get_rl_data,
    REPO_DIR,
    BIN_DIR,
    log_info,
    log_error,
    log_success,
    check_required_commands,
    run_command,
    is_process_running,
    ensure_dir,
)
from config import get_steam_path, set_launch_options

RUNNER_PATH = f"{BIN_DIR}/bakkesmod"
CONFIG_FILE = f"{CONFIG_DIR}/repo_path"
DOWNLOAD_URL = "https://github.com/bakkesmodorg/BakkesModInjectorCpp/releases/latest/download/BakkesModSetup.zip"
REQUIRED_COMMANDS = ["mkdir", "rm", "curl", "killall", "sleep"]


def save_repo_path() -> bool:
    ensure_dir(CONFIG_DIR)

    try:
        with open(CONFIG_FILE, "w") as f:
            _ = f.write(REPO_DIR)
        log_success(f"Saved repository path: {REPO_DIR}")
        return True
    except Exception as e:
        log_error(f"Failed to save repo path: {e}")
        return False


def download_bakkesmod_setup() -> str | None:
    zip_path = f"{REPO_DIR}/BakkesModSetup.zip"
    extract_dir = f"{REPO_DIR}/BakkesModSetup"

    log_info(f"Downloading BakkesModSetup.zip from {DOWNLOAD_URL}")

    # write temp zip file
    try:
        response = requests.get(DOWNLOAD_URL, stream=True)
        response.raise_for_status()

        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                _ = f.write(chunk)

        ensure_dir(extract_dir)

        log_info("Extracting BakkesModSetup.zip")

        # extract the installer
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        # remove temp zip
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


def setup_prefix_and_install(setup_exe_path: str, platform: str) -> bool:
    wait_process_exit("RocketLeague.exe", "Waiting for RocketLeague to exit")

    # attempt to get data from the platform
    data = get_rl_data(platform)
    if not data:
        log_error(f"Failed to get Rocket League data from {platform}")
        return False

    # deconstruct data
    wine_prefix, wine_bin = data

    log_info("Configuring prefix to Windows 10")

    # set prefix to windows 10 (og BakkesLinux does that so why not)
    wine_cmd = f'WINEFSYNC=1 WINEPREFIX="{wine_prefix}" "{wine_bin}" winecfg /v win10'
    _ = run_command(wine_cmd, True, debug=True)

    log_info("Running BakkesMod setup executable")

    # add exec permission to executable
    setup_exe = Path(setup_exe_path, "BakkesModSetup.exe")
    os.chmod(setup_exe, 0o755)

    # run the bakkesmod setup with the platform prefix/bin
    install_cmd = f'WINEFSYNC=1 WINEPREFIX="{wine_prefix}" "{wine_bin}" "{setup_exe}"'
    if not run_command(install_cmd, debug=True):
        log_error("Failed to run BakkesMod setup")
        return False

    # now save the prefix data to config folder
    platform_config_path = f"{CONFIG_DIR}/{platform}"
    with open(platform_config_path, "w") as f:
        _ = f.write(f"WINE_PREFIX={wine_prefix}\nWINE_BINARY={wine_bin}")

    return True


def create_bakkesmod_symlink() -> bool:
    log_info(f"Creating bakkesmod symlink at {RUNNER_PATH}")

    runner_script = f"{REPO_DIR}/src/runner.sh"

    # shouldn't happen
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


def create_desktop_file(platform: str) -> bool:
    desktop_filename = f"bakkesmod-{platform}.desktop"
    desktop_path = f"{DESKTOP_DIR}/{desktop_filename}"

    log_info(f"Creating desktop file for {platform} at {desktop_path}")

    desktop_content = f"""[Desktop Entry]
Name=BakkesMod ({platform.title()})
Comment=Bakkesmod for Rocket League ({platform.title()})
Exec={RUNNER_PATH} run --standalone --platform="{platform}"
Icon=applications-games
Terminal=false
Type=Application
Categories=Game;
"""

    try:
        with open(desktop_path, "w") as f:
            _ = f.write(desktop_content)

        os.chmod(desktop_path, 0o644)
        log_success(f"Desktop file created successfully: {desktop_filename}")
        return True
    except Exception as e:
        log_error(f"Failed to create desktop file: {e}")
        return False


def setup_launch_options(steam_path: str) -> None:
    response = input(
        "Do you want to set launch options for RocketLeague? (y/n) "
    ).lower()

    if response == "y":
        wait_process_exit("steam", "Waiting for Steam to exit")
        if set_launch_options(RUNNER_PATH, steam_path):
            log_success("Launch options set successfully")
        else:
            log_error("Failed to set launch options")
    elif response == "n":
        log_info("Skipping launch options setup")
    else:
        log_error("Invalid response")


def install() -> int:
    os.environ["WINEDEBUG"] = "-all"

    # ensure we have the required commands
    if not check_required_commands(REQUIRED_COMMANDS):
        return 1

    log_info("Creating directories...")
    ensure_dir(CONFIG_DIR)
    ensure_dir(BIN_DIR)
    ensure_dir(DESKTOP_DIR)

    # save repo path
    if not save_repo_path():
        return 1

    setup_dir = download_bakkesmod_setup()
    if not setup_dir:
        return 1

    parser = argparse.ArgumentParser(description="BakkesMod Installer")
    _ = parser.add_argument("--platform", choices=["steam", "heroic"])

    args = parser.parse_args()
    platform: str = args.platform or "steam"

    # create prefix for the desired platform
    if not setup_prefix_and_install(setup_dir, platform):
        return 1

    # create symlink
    if not create_bakkesmod_symlink():
        return 1

    # create desktop file
    if not create_desktop_file(platform):
        return 1

    # setup launch options for steam
    if platform == "steam":
        steam_path = get_steam_path()
        setup_launch_options(steam_path)
    else:
        log_info("skipping launch options setup")

    log_success("Installation complete!")
    log_info("You can now run 'bakkesmod' from anywhere")

    return 0


if __name__ == "__main__":
    sys.exit(install())
