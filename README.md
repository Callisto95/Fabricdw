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
python -m fabricdw <installation name> # this can now be anywhere
```

A shell alias can be created, using the venv python installation: `alias fabricdw="<INSTALLATION_DIR>/venv/bin/python -m fabricdw"`.

A more advanced approach would be this function (in your shell's rc file):

```bash
fabricdw() {
        if [[ -f "fabricdw" ]]; then
                ./fabricdw $*
        else
                <INSTALLATION_DIR>/venv/bin/python -m fabricdw $*
        fi
}
```

If in a directory with a Fabricdw installation, it uses the installation, otherwise it runs the installation script.

Installing to the global and user directory is possible (via `pip install .` or `pip install --user .` respectively), but this can break system packages.

### Options

Default options are in `[]` after each option.

#### Fabricdw itself

- `{ list | create | remove }`: lists, creates, or removes an installation

- `-d`|`--directory`: path of the installation. [`<current directory>/<installation name>`]

#### Server

- `-u`|`--user`: the user running the server. [current user]
- `-mn`|`--min-ram`: minimum amount of RAM the server can use (in GB). [`defaults.min_ram` or `0.5`]
- `-mx`|`--max-ram`: maximum amount of RAM the server can use (in GB). [`defaults.max_ram` or `6`]
- `-b`|`--backups`: the amount of backups to keep. [`defaults.backups` or `5`]
- `-i`|`--idle-time`: the amount of seconds after which the server is counted as "idle". `0` to disable the server going idle. [`defaults.idle_time` or `0`]
- `--show-init-output`: show the output of the initialization. [no output]
- `--absolute-paths`: use absolute path when defining `SERVER_ROOT` and `BACKUP_DEST`. [`$(pwd)` command]
- `--java`: change the java executable. [`java` in `PATH`]
- `--java-args`: arguments for the JRE. Separated by commas (e.g. `-XX:+UseZGC,-XX:+ZGenerational`). [no arguments]

#### Game

Any property in the `server.properties` file can be changed with the `-p`|`--property` argument. Just like the properties file, the argument also uses the `<KEY>=<VALUE>` syntax (e.g. `--property difficulty=hard`).

See the [Minecraft Wiki](https://minecraft.wiki/w/Server.properties#Default_content) for reference.
