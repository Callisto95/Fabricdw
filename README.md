# Fabricdw

`fabricd` wrapper

This is a python script which allows you to easily create multiple Minecraft Fabric servers on one server.

`fabricdw` handles the required environment variables for multiple fabric servers. It generates the required wrapper file, which is used to interact with a specific server.

`fabricdw` requires `fabricd`, which is the [minecraft-server](https://github.com/Edenhofer/minecraft-server/) script installed with `GAME=fabric` and `INAME=fabricd`.

## Note for `fabricd`

`fabricd`, also comes with the AUR package [fabric-server](https://aur.archlinux.org/packages/fabric-server).

## Installation

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running Fabricdw

```shell
source venv/bin/activate # you must be in the virtual environment
python -m fabricdw # this can now be anywhere
```

A shell alias can be created, using the venv python installation: `alias fabricdw="<installation dir>/venv/bin/python -m fabricdw"`.

Installing to the global and user directory is possible (via `pip install .` or `pip install --user .` respectively), but this can break system packages.

### Options

Default options are in `[]` after each option.

#### Server

- `-d`|`--directory`: path of the installation. [current directory]
- `-r`|`--remove`: remove the installation (you're asked before any files are removed)
- `-u`|`--user`: the user running the server. [current user]
- `-mn`|`--min-ram`: minimum amount of RAM the server can use (in GB). [`defaults.min_ram` or `0.5`]
- `-mx`|`--max-ram`: maximum amount of RAM the server can use (in GB). [`defaults.max_ram` or `6`]
- `-p`|`--port`: the port the server will use. [`25565`]
- `-b`|`--backups`: the amount of backups to keep. [`defaults.backups` or `5`]
- `-i`|`--idle-time`: the amount of seconds after which the server is counted as "idle". `0` to disable the server going idle. [`defaults.idle_time` or `0`]
- `--show-init-output`: show the output of the initialization. [no output]

#### Game

- `-w`|`--world-name`: name of the minecraft world. [`world`]
- `-s`|`--seed`: the seed for the minecraft world. [random seed]
- `-df`|`--difficulty`: the difficulty for the server. [`defaults.difficulty` or `normal`]
- `-gm`|`--gamemode`: the game mode (e.g. survival, creative) for the server. [`defaults.gamemode` or `survival`]
