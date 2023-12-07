# Fabricdw

`fabricd` wrapper

This is a python script which allows you to easily create multiple Minecraft Fabric servers on one server.

`fabricdw` handles the required environment variables for multiple fabric servers. It generates the required wrapper file, which is used to interact with a specific server.

`fabricdw` requires `fabricd`, which is the [minecraft-server](https://github.com/Edenhofer/minecraft-server/) script installed with `GAME=fabric` and `INAME=fabricd`.

## Note for `fabricd`
`fabricd`, also comes with the AUR package [fabric-server](https://aur.archlinux.org/packages/fabric-server).

## Usage

```shell
./fabric-installer.py <name of the installation>
```
It is highly recommended to either use the `-d`|`--directory` argument to change the installation directory.

After an installation is created, a `fabricdw` file is created in the installation directory.
This file passes the required environment variables to `fabricd`. Any arguments are passed to `fabricd`.

### Options

These options are the arguments for the `fabric-installer.py` script:

- `-d`|`--directory`: path of the installation. Default: current directory
- `-mn`|`--min-ram`: minimum amount of RAM the server can use (in GB). Default: `default_min_ram` in config file or `0.5`
- `-mx`|`--max-ram`: maximum amount of RAM the server can use (in GB). Default: `default_max_ram` in config file or `6`
- `-p`|`--port`: the port the server will use. Default: `25565`
- `-a`|`--autoinit`: when a new installation is run for the first time, it has to initialize. This option automatically does that. Default: does not initialize server
- `--show-init-output`: show the output of the initialization, if `-a` or `--autoinit` is given. Default: output is hidden
- `-r`|`--remove`: remove the installation (you're asked before any files are removed)
