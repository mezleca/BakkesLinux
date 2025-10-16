import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

# game identifiers
STEAM_APP_ID = "252950"
HEROIC_CODENAME = "Sugar"


def get_home_dir() -> str:
    return str(Path.home())


# extra consts
HOME = get_home_dir()
REPO_DIR = str(Path(__file__).parent.parent.absolute())
CONFIG_DIR = f"{HOME}/.local/share/BakkesLinux"
BIN_DIR = f"{HOME}/.local/bin"
DESKTOP_DIR = f"{HOME}/.local/share/applications"


def log_info(msg: str) -> None:
    print(f"[INFO] {msg}")


def log_error(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)


def log_success(msg: str) -> None:
    print(f"[SUCCESS] {msg}")


def log_debug(msg: str) -> None:
    print(f"[DEBUG] {msg}")


def check_command(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def check_required_commands(commands: list[str]) -> bool:
    log_info("Checking required commands...")
    missing: list[str] = []

    for cmd in commands:
        if not check_command(cmd):
            missing.append(cmd)

    if missing:
        log_error(f"Missing required commands: {', '.join(missing)}")
        return False

    log_success("All required commands are available")
    return True


def run_command(
    cmd: str, check: bool = True, capture: bool = False, debug: bool = False
) -> str | bool | None:
    try:
        if debug:
            log_info(f"cmd: {cmd}")

        if capture:
            result = subprocess.run(
                cmd, shell=True, check=check, capture_output=True, text=True
            )
            return result.stdout.strip()
        else:
            result = subprocess.run(cmd, shell=True, check=check)
            return result.returncode == 0
    except subprocess.CalledProcessError as e:
        log_error(f"Command failed: {cmd}")
        log_error(f"Error: {e}")
        return None if capture else False


def is_process_running(process_name: str) -> bool:
    result = run_command(f"pgrep '{process_name}'", check=False, capture=True)
    return result is not None and result != ""


def get_pid(process_name: str) -> str | bool | None:
    return run_command(f"pgrep {process_name}", check=False, capture=True)


def wait_process_exit(pid: int | str) -> None:
    _ = run_command(f"tail --pid={pid} -f /dev/null", check=False)


def kill_process(pid: int | str) -> str | bool | None:
    return run_command(f"kill {pid} 2>/dev/null", check=False)


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def get_proton_path(home: str) -> str | None:
    if home == "":
        home = get_home_dir()

    rl_prefix = f"{home}/.steam/steam/steamapps/compatdata/252950"
    config_info = Path(rl_prefix, "config_info")

    if not config_info.exists():
        log_error(f"config_info not found: {config_info}")
        log_error("make sure Rocket League is installed on steam")
        return None

    with open(config_info, "r") as f:
        lines = f.readlines()
        if len(lines) < 3:
            log_error("Invalid config_info format")
            return None

        proton_path = Path(lines[2].strip()).parent
        return str(proton_path)


def get_steam_data() -> tuple[str, str] | None:
    proton_path = get_proton_path("")
    if not proton_path:
        return None

    prefix = f"{HOME}/.steam/steam/steamapps/compatdata/{STEAM_APP_ID}/pfx"
    wine = f"{proton_path}/bin/wine64"

    return prefix, wine


# @TOFIX: can users change heroic installation? idk
def get_heroic_data() -> tuple[str, str] | None:
    config_content = ""
    with open(f"{HOME}/.config/heroic/GamesConfig/{HEROIC_CODENAME}.json", "r") as c:
        config_content = c.read()

    config_data = json.loads(config_content)[HEROIC_CODENAME]
    wine_data = config_data["wineVersion"]
    prefix = f"{config_data['winePrefix']}/pfx"
    wine = (
        str(Path(f"{wine_data['bin']}/../files/bin/wine64").resolve())
        if wine_data["type"] == "proton"
        else wine_data["bin"]
    )
    return prefix, wine


def get_rl_data(platform: str) -> tuple[str, str] | None:
    match platform:
        case "steam":
            return get_steam_data()
        case "heroic":
            return get_heroic_data()
        case _:
            pass
    return None


def parse_config_file(location: str) -> dict[str, str] | None:
    data: dict[str, str] = {}
    if not os.path.exists(location):
        log_error(f"failed to find platform config at: {location}")
        return None

    with open(location) as f:
        for line in f:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key] = value

    return data


def get_config_data(platform: str) -> tuple[str, str] | None:
    config = parse_config_file(f"{CONFIG_DIR}/{platform}")
    if not config:
        return None

    return config["WINE_PREFIX"], config["WINE_BINARY"]


# test
if __name__ == "__main__":
    print(get_rl_data("steam"))
    print(get_rl_data("heroic"))
    print(get_config_data("heroic"))
