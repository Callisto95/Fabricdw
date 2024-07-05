import os
import stat
import subprocess
from argparse import Namespace

import requests
from colorama import Fore, Style
from requests import Response

from fabricdw.common import absolute_path, CONFIG, Installation, ask_okay_to_write_into, remove_dir, convert_bool
from fabricdw.common.properties import Defaults, Properties
from fabricdw.installations.fabric import select_version
from fabricdw.properties import modify_properties

SERVER_JAR_FILE: str = "fabric-server-launch.jar"
LAUNCH_COMMAND: str = ("{java_executable}{java_args} -Dlog4j2.formatMsgNoLookups=true -Xms{min_ram}M -Xmx{max_ram}M "
					   "-jar ./fabric-server-launch.jar nogui")
FABRIC_ENV_FILE: str = "fabricdw"


def set_property_if_not_defined(args: Namespace, prop_name: str, fallback: str) -> None:
	if prop_name not in args.properties:
		args.properties[prop_name] = fallback


def create_installation(args: Namespace) -> None:
	active_installation: Installation = CONFIG.get_installation(args.name)
	
	if active_installation is not None:
		print(
			f"{Fore.RED}installation '{active_installation.pretty_name(Fore.RED)}' already exists!"
			f"({active_installation.root}){Style.RESET_ALL}"
		)
		return
	
	os.makedirs(args.output_dir, exist_ok=True)
	active_dir: str = absolute_path(args.output_dir)
	
	# required by the installer
	set_property_if_not_defined(args, Properties.WORLD_NAME, Defaults.WORLD_NAME)
	set_property_if_not_defined(args, Properties.PORT_SERVER, Defaults.PORT_SERVER)
	
	try:
		_dir = _create_installation(args, active_dir)
		
		print(f"installation '{Installation.pretty_name_str(args.name)}' created! ({active_dir})")
		
		CONFIG.add_installation(args.name, _dir)
		
		return
	except KeyboardInterrupt as kbe:
		print("Keyboard interrupt: Cleaning up...")
		remove_dir(active_dir)
		raise kbe


def format_java_args(args: str) -> str:
	if len(args) == 0:
		return ""
	
	return f" {args.replace(', ', ' ')}"


def _create_installation(
	args: Namespace, active_dir: str, init_server: bool = True, directory_can_be_filled: bool = False
) -> str | None:
	if not directory_can_be_filled and not ask_okay_to_write_into:
		return None
	
	if init_server:
		initialize_server(args, active_dir)
	
	create_fabricdw_script(args, active_dir)
	
	modify_properties(active_dir, args.properties)
	
	return active_dir


def initialize_server(args: Namespace, active_dir: str) -> None:
	server_url: str = select_version()
	
	server_jar: Response = requests.get(server_url)
	
	jar_file: str = f"{active_dir}/{SERVER_JAR_FILE}"
	
	with open(jar_file, "wb") as jar:
		jar.write(server_jar.content)
	
	print("initializing the server...")
	print(f"{Fore.RED}{Style.BRIGHT}This should not actually start the server!{Style.RESET_ALL}")
	subprocess.call(["java", "-jar", jar_file], cwd=active_dir, stdout=args.init_output)


def create_fabricdw_script(args: Namespace, active_dir: str) -> None:
	fabric_env_file = f"{active_dir}/{FABRIC_ENV_FILE}"
	launch_command = LAUNCH_COMMAND.format(
		java_executable=args.java_executable,
		java_args=format_java_args(args.java_args),
		min_ram=int(args.min_ram * 1024),
		max_ram=int(args.max_ram * 1024)
	)
	world_name = args.properties[Properties.WORLD_NAME]
	port = args.properties[Properties.PORT_SERVER]
	
	server_dir: str = active_dir if args.absolute_paths else "$(pwd)"
	
	with open(fabric_env_file, 'w') as launch_script_file:
		launch_script_file.write(
			f"""#!/bin/sh
	GAME_USER="{args.user}" \\
	IDLE_SERVER="{convert_bool(args.idle_time != 0)}" \\
	IDLE_IF_TIME="{900 if args.idle_time == 0 else args.idle_time}" \\
	SERVER_ROOT="{server_dir}" \\
	BACKUP_DEST="{server_dir}/backup" \\
	BACKUP_PATHS="{world_name} {world_name}_nether {world_name}_the_end" \\
	KEEP_BACKUPS="{args.backups}" \\
	SESSION_NAME="{args.name}" \\
	GAME_PORT="{port}" \\
	SERVER_START_CMD="{launch_command}" \\
	fabricd $*
		"""
		)
	
	# to run fabricdw, it must be executable
	# give the EXEC flag to the file
	os.chmod(fabric_env_file, os.stat(fabric_env_file).st_mode | stat.S_IEXEC)
