import vdf
import os
from pathlib import Path
from utils import log_info, log_error, log_success

ROCKET_LEAGUE_APP_ID = "252950"


def get_steam_path() -> str:
    return os.path.expanduser("~/.steam/steam")


def get_userdata_path(steam_path: str | None) -> str:
    if steam_path is None:
        steam_path = get_steam_path()
    return str(Path(steam_path, "userdata"))


def get_first_user_id(steam_path: str) -> str | None:
    userdata = get_userdata_path(steam_path)

    try:
        userid = next(os.scandir(userdata)).path
        return userid
    except StopIteration:
        log_error("No Steam user found in userdata directory")
        return None


def get_config_path(userid: str) -> Path:
    return Path(userid, "config/localconfig.vdf")


def set_launch_options(bakkes_script_path: str, steam_path: str) -> bool:
    log_info("Setting Rocket League launch options in Steam")

    userid = get_first_user_id(steam_path)
    if userid is None:
        return False

    config_path = get_config_path(userid)

    if not config_path.exists():
        log_error(f"Config file not found: {config_path}")
        return False

    try:
        with open(config_path, "r") as config_file:
            config = vdf.load(config_file)

        rl_config = config["UserLocalConfigStore"]["Software"]["Valve"]["Steam"][
            "apps"
        ][ROCKET_LEAGUE_APP_ID]

        # get old parameters
        old_launch_options = rl_config.get("LaunchOptions", "")

        if old_launch_options:
            log_info(f"Previous launch options: {old_launch_options}")

            # check if bakkes is alredy placed on the launch parameters
            if bakkes_script_path in old_launch_options:
                return True

            # add bakkes before %command% if present
            if "%command%" in old_launch_options:
                new_launch_options = old_launch_options.replace(
                    "%command%", f'"{bakkes_script_path}" & %command%'
                )
            else:
                # if %command% is not present, add it
                new_launch_options = (
                    f'{old_launch_options} "{bakkes_script_path}" & %command%'
                )
        else:
            new_launch_options = f'"{bakkes_script_path}" & %command%'

        rl_config["LaunchOptions"] = new_launch_options

        with open(config_path, "w") as config_file:
            vdf.dump(config, config_file, pretty=True)

        log_success(f"New launch options: {new_launch_options}")
        return True
    except Exception as e:
        log_error(f"Failed to set launch options: {e}")
        return False
