# BakkesLinux - Automated BakkesMod for Linux

fork of [BakkesLinux](https://github.com/CrumblyLiquid/BakkesLinux) that uses Python to automate BakkesMod installation and execution on Linux. includes some modifications to make the whole process easier.

## Installation

```bash
# clone and install for Steam (default)
git clone https://github.com/mezleca/BakkesLinux
cd BakkesLinux
./run.sh install --platform="steam"

# for other platforms
# supported platforms: steam, heroic
./run.sh install --platform="heroic"
```

## Usage

```bash
# run BakkesMod (waits for RL to start)
bakkesmod run

# run standalone (without RL checks)
bakkesmod run --standalone

# update or remove
bakkesmod update
bakkesmod remove
```

## Features

- downloads and installs BakkesMod automatically
- sets up wine prefixes and launch options (steam)
- creates desktop shortcuts

## Requirements

- Python 3
- Rocket League installed on any of the supported platform

## Troubleshooting

**BakkesMod won't inject**: disable "Enable safe mode" in BakkesMod settings

**WINEFSYNC errors**: ensure both Rocket League and BakkesMod use the same sync mode

**Flatpak issues**: use non-Flatpak versions of Steam/protontricks if possible

for more details, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Steam Deck

works on Steam Deck! install in Desktop Mode following the same steps. see [STEAMDECK.md](STEAMDECK.md) for tips.

## Manual Installation (Original Method)

if you prefer the manual approach or want to understand how it works, check the original [BakkesLinux guide](https://github.com/CrumblyLiquid/BakkesLinux).

### Download BakkesMod
download `BakkesModSetup.zip` from the [official website](https://bakkesmod.com/) or [GitHub repository](https://github.com/bakkesmodorg/BakkesModInjectorCpp/releases).

### Finding wine prefix
you'll need to find what [wine prefix](https://wiki.archlinux.org/title/wine#WINEPREFIX) the game is running in.

on Steam this is usually `~/.steam/steam/steamapps/compatdata/252950/pfx` (note that the AppID of Rocket League on Steam is `252950`).

### Finding Wine/Proton folder
you'll need to find the path to Proton/Wine that is used for Rocket League.

on Steam this can be achieved by inspecting `~/.steam/steam/steamapps/compatdata/252950/config_info` and noting the path on the 3. line without the last directory (the result should end with `/dist`).

you can achieve that with this command: `sed -n 3p ~/.steam/steam/steamapps/compatdata/252950/config_info | xargs -d '\n' dirname`

### Installation
1. configure wine prefix to Windows 10: `WINEPREFIX="your_prefix" winecfg` and set `Windows Version` to `Windows 10`
2. run BakkesModSetup.exe: `WINEPREFIX="your_prefix" "wine_folder/bin/wine64" ~/Downloads/BakkesModSetup.exe`
3. after starting Rocket League, launch BakkesMod: `WINEPREFIX="your_prefix" "wine_folder/bin/wine64" "your_prefix/drive_c/Program Files/BakkesMod/BakkesMod.exe"`

## Contributing

feel free to submit issues or pull requests if you encounter problems or have suggestions for improvements.
