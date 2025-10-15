import sys
import subprocess
import shutil
from pathlib import Path


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
    cmd: str, check: bool = True, capture: bool = False
) -> str | bool | None:
    try:
        if capture:
            log_info(f"executing: {cmd}")
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
    result = run_command(f"pgrep -f '{process_name}'", check=False, capture=True)
    return result is not None and result != ""


def get_pid(process_name: str) -> str | bool | None:
    return run_command(f"pgrep {process_name}", check=False, capture=True)


def wait_process_exit(pid: int | str) -> None:
    _ = run_command(f"tail --pid={pid} -f /dev/null", check=False)


def kill_process(pid: int | str) -> str | bool | None:
    return run_command(f"kill {pid} 2>/dev/null", check=False)


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def get_home_dir() -> str:
    return str(Path.home())


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
