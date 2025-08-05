# Fabricdw

`fabricd` wrapper

This is a python script which allows you to easily create multiple Minecraft Fabric servers on one server.

`fabricdw` handles the required environment variables for multiple fabric servers. It generates the required wrapper file, which is used to interact with a specific server.

`fabricdw` requires `fabricd`, which is the [minecraft-server](https://github.com/Edenhofer/minecraft-server/) script installed with `GAME=fabric` and `INAME=fabricd` (as far as I can tell).

## Note for `fabricd`

`fabricd`, also comes with the AUR package [fabric-server](https://aur.archlinux.org/packages/fabric-server).

## Installation

```shell
pip install -r requirements.txt
```

If your pip is system wide, this may cause issues regarding `externally-managed-environment`.

You can either use a virtual environment instead or install them via pacman / the AUR.

Here is the venv approach:

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If a venv is used, replace the generic `python` with `[INSTALLATION_DIRECTORY]/venv/bin/python` in the next commands.

## Running Fabricdw

```shell
# this can now be anywhere
PYTHONPATH=[INSTALLATION_DIRECTORY] python -m fabricdw
```

A more advanced approach would be this function (in your shell's rc file):

```bash
fabricdw() {
        if [[ -f "fabricdw" ]]; then
                ./fabricdw $*
        else
                PYTHONPATH=[INSTALLATION_DIRECTORY] python -m fabricdw $*
        fi
}
```

If in a directory with a Fabricdw installation, it uses the installation, otherwise it runs the installation script.

### Options

Default options are in `[]` after each option.

#### Fabricdw itself

Modes: `{ create | remove | copy | move | rename | update | list }`

Each mode has different arguments. Check them with `[mode] --help`.

##### Create

- `name`: name of the installation to create
- `-d`|`--directory`: path of the installation. [`[current directory]/[installation name]`]
- `-p`|`--property`: changes a property within the `server.properties` file. See [Minecraft Wiki](https://minecraft.wiki/w/Server.properties#Default_content). [no changes]
- `-u`|`--user`: the user running the server. [current user]
- `-m`|`--min-ram`: minimum amount of RAM the server can use (in GB). [`defaults.min_ram` or `0.5`]
- `-x`|`--max-ram`: maximum amount of RAM the server can use (in GB). [`defaults.max_ram` or `6`]
- `-b`|`--backups`: the amount of backups to keep. [`defaults.backups` or `5`]
- `-i`|`--idle-time`: the amount of seconds after which the server is counted as "idle". `0` to disable the server going idle. [`defaults.idle_time` or `0`]
- `--show-init-output`: show the output of the initialization. [no output]
- `--allow-non-empty`: skips the question, whether the target directory can be empty. [ask]
- `--allow-snapshots`: show snapshot game versions in selection. Does not influence `--game-version [version]`, but affects `--game-version latest`. [only releases]
- `--allow-unstable`: show unstable loader and installer versions in selection. Does not influence `--{loader,installer}-version [version]`, but affects `--{loader,installer}-version latest`. [only stable]
- `--game-version`: can be `ask`, `latest`, or an actual version. [`ask`]
- `--loader-version`: can be `ask`, `latest`, or an actual fabric loader version. [`latest`]
- `--fabric-version`: can be `ask`, `latest`, or an actual fabric installer version. [`latest`]
- `--java`: change the java executable. [`java` in `PATH`]
- `--java-args`: arguments for the JRE. Separated by commas (e.g. `-XX:+UseZGC,-XX:+ZGenerational`). [no arguments]

##### Delete

- `name`: name of the installation to delete
- `--yes-just-delete`: skip the question, whether the installation should really be deleted

##### Copy

- `source`: installation to be copied
- `target`: name of the new installation
- `-d`|`--directory`: path of the installation. [`[current directory]/[installation name]`]

##### Move

- `source`: installation to be moved
- `output_dir`: directory, into which the installation will be moved. [`[current directory]/[installation name]`]

##### Rename

- `source`: installation to be renamed
- `target`: new name of the installation

##### Update

  Inherits all options from `Create`.

- `--keep-backups`: do not delete backups, which are created during the update process. [remove backups]

##### Import

  Adds an already existing installation, which Fabricdw is not aware of.

- `name`: name of the imported installation
- `output_dir`: directory, of the already existing installation. [`[current directory]/[installation name]`]

##### List

Always lists all installations and the server root.

- `--verify`: verify the existence of the all installations, remove the non-existent ones from the saved list.
