#!/usr/bin/env python3

import os
from random import choices
import sys
import time
import argparse
from pathlib import Path
from utils import (
    get_config_data,
    get_proton_path,
    log_info,
    log_error,
    log_debug,
    is_process_running,
    get_pid,
    wait_process_exit,
    kill_process,
)

HOME = str(Path.home())
WINESYNC = "WINEFSYNC=1"


def check_bakkes_exists(executable: str) -> bool:
    if not Path(executable).exists():
        log_error(f"{executable} doesn't exist! ABORTING!")
        return False
    return True


def wait_for_rocket_league() -> str | bool | None:
    log_info("Waiting for Rocket League to start...")

    while not is_process_running("RocketLeague"):
        time.sleep(1)

    game_pid = get_pid("RocketLeague")
    log_info(f"Rocket League detected (PID: {game_pid})")
    return game_pid


def launch_bakkesmod(wine: str, prefix: str, executable: str):
    log_info("Launching BakkesMod...")

    wine_env = f"{WINESYNC}"

    log_debug(f"Using {wine_env}")

    cmd = f'{wine_env} WINEPREFIX="{prefix}" "{wine}" "{executable}" &'

    log_debug(f"Command: {cmd}")

    _ = os.system(cmd)
    time.sleep(2)

    if is_process_running("BakkesMod.exe"):
        bakkes_pid = get_pid("BakkesMod.exe")
        log_info(f"BakkesMod started successfully (PID: {bakkes_pid})")
        return bakkes_pid
    else:
        log_error("Failed to start BakkesMod")
        return None


def monitor_rocket_league(game_pid: int | str, bakkes_pid: int | str):
    log_info("Monitoring Rocket League process...")

    wait_process_exit(game_pid)

    log_info("Rocket League closed, killing BakkesMod...")

    if kill_process(bakkes_pid):
        log_info("BakkesMod closed successfully")
    else:
        log_debug("BakkesMod process already terminated")


def run_bakkesmod(skip_checks: bool = False, platform: str = ""):
    data = get_config_data(platform)

    if not data:
        return 1

    prefix, wine = data

    # ensure bakkesmod in installed
    bakkes_exe = f"{prefix}/drive_c/Program Files/BakkesMod/BakkesMod.exe"
    if not check_bakkes_exists(bakkes_exe):
        return 1

    log_info(f"BakkesMod path: {bakkes_exe}")
    log_info(f"Skip checks: {skip_checks}")
    log_info(f"Platform: {platform}")

    if is_process_running("BakkesMod.exe"):
        log_info("BakkesMod is already running, exiting...")
        return 0

    game_pid = None

    if not skip_checks:
        game_pid = wait_for_rocket_league()
    else:
        log_info("Running in standalone mode (no RL checks)")

    bakkes_pid = launch_bakkesmod(wine, prefix, bakkes_exe)

    if not bakkes_pid:
        return 1

    if not skip_checks and game_pid:
        monitor_rocket_league(game_pid, bakkes_pid)
    else:
        log_info("BakkesMod is running in background")
        log_info("Use 'pkill -f BakkesMod.exe' to close it manually")

    return 0


def main():
    parser = argparse.ArgumentParser(description="BakkesMod")
    _ = parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Run in standalone mode without RL checks",
    )
    _ = parser.add_argument("--platform", choices=["steam", "heroic"])
    _ = parser.add_argument(
        "--standalone", action="store_true", help="Alias for --skip-checks"
    )

    args = parser.parse_args()

    skip_checks: bool = args.skip_checks or args.standalone
    platform: str = args.platform

    sys.exit(run_bakkesmod(skip_checks, platform))


if __name__ == "__main__":
    main()
