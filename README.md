# BakkesLinux

fork of [BakkesLinux](https://github.com/CrumblyLiquid/BakkesLinux) that aims to automate BakkesMod installation and execution on Linux. also includes some modifications to make the whole process easier.

## Installation

```bash
# clone and install for Steam (default)
# warn: this repository must be kept in the same location it was cloned 
# otherwise run.sh link will broken
git clone https://github.com/mezleca/BakkesLinux
cd BakkesLinux

# install 
# supported platforms: steam, heroic
./run.sh install --platform="steam"
```

## Usage (Terminal)

after the installation process, you can either use `./run.sh` from the repository folder or `bakkesmod` from anywhere:

```bash
# run bakkesmod (waits for RL to start)
bakkesmod run

# run standalone (without RL checks)
bakkesmod run --standalone

# run for specific platform
bakkesmod run --platform="heroic"

# update or remove
bakkesmod update
```

> install also creates a .desktop file so you can open bakkesmod using your DE app launcher

> [!WARNING]
> **Heroic Users**: If BakkesMod shows "outdated version" or doesn't inject even with Rocket League open, disable "Enable Safe Mode" in BakkesMod options.

## Features

- downloads and installs BakkesMod automatically
- sets up wine prefixes and launch options (steam)
- creates desktop shortcuts

## Requirements

- Python 3
- Rocket League installed on any of the supported platform

# TODO
- [ ] temp copy / link bakkesmod installation to prefix (so you dont need to reinstall bakkesmod on new prefixes)

## Troubleshooting

**BakkesMod won't inject**: disable "Enable safe mode" in BakkesMod settings

**WINEFSYNC errors**: ensure both Rocket League and BakkesMod use the same sync mode

**Flatpak issues**: use non-Flatpak versions of Steam/protontricks if possible

for more details, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Manual Installation (Original Method)

if you prefer the manual approach or want to understand how it works, check the original [BakkesLinux guide](https://github.com/CrumblyLiquid/BakkesLinux).

## Contributing

feel free to submit issues or pull requests if you encounter problems or have suggestions for improvements.
