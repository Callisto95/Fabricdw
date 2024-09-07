import os
import stat
import subprocess

from colorama import Fore, Style

from fabricdw.args import args
from fabricdw.common import ask_okay_to_write_into, CONFIG, convert_bool_to_str, FABRICD_ENV_FILE, Installation, remove_dir, \
	SERVER_JAR_FILE
from fabricdw.common.properties import Defaults, Properties
from fabricdw.installations.fabric import select_and_download_version
from fabricdw.properties import modify_properties

LAUNCH_COMMAND: str = ("{java_executable} {java_args} -Dlog4j2.formatMsgNoLookups=true -Xms{min_ram}M -Xmx{max_ram}M "
					   "-jar ./fabric-server-launch.jar nogui")


def set_property_if_not_defined(prop_name: str, fallback: str) -> None:
	if prop_name not in args().properties:
		args().properties[prop_name] = fallback


def create_installation() -> None:
	Installation.ensure_does_not_exist(args().name)
	
	installation_directory: str = args().output_dir
	
	try:
		os.makedirs(installation_directory, exist_ok=True)
		
		if not ask_okay_to_write_into(message_if_cancelled="cancelling installation"):
			return
		
		select_and_download_version()
		
		initialize_server()
		
		modify_properties()
		
		create_fabricdw_script()
		
		CONFIG.create_new_installation(args().name, installation_directory)
		
		return
	except KeyboardInterrupt as kbe:
		if remove_dir(installation_directory):
			print("Interrupted! Cleaning up...")
		raise kbe


def format_java_args(arguments: str) -> str:
	if len(arguments) == 0:
		return ""
	
	return f"{arguments.replace(', ', ' ')}"


def initialize_server(installation_directory: str = None) -> None:
	if not installation_directory:
		installation_directory = args().output_dir
	
	print("Initializing the server...")
	print(f"{Fore.RED}{Style.BRIGHT}This should not actually start the server!{Style.RESET_ALL}")
	# TODO: timeout?
	subprocess.call(["java", "-jar", SERVER_JAR_FILE], cwd=installation_directory, stdout=args().init_output)


def create_fabricdw_script(installation_directory: str = None) -> None:
	if not installation_directory:
		installation_directory = args().output_dir
	
	fabric_env_file: str = f"{installation_directory}/{FABRICD_ENV_FILE}"
	launch_command: str = LAUNCH_COMMAND.format(
		java_executable=args().java_executable,
		java_args=format_java_args(args().java_args),
		min_ram=int(args().min_ram * 1024),
		max_ram=int(args().max_ram * 1024)
	)
	
	world_name = args().properties[
		Properties.WORLD_NAME] if Properties.WORLD_NAME in args().properties else Defaults.WORLD_NAME
	port = args().properties[
		Properties.PORT_SERVER] if Properties.PORT_SERVER in args().properties else Defaults.PORT_SERVER
	
	with open(fabric_env_file, 'w') as launch_script_file:
		# Note:
		# BACKUP_PATHS is multiple folders. New versions do not use multiple world directories.
		# This is fine. tar handles this.		
		launch_script_file.write(
			f"""#!/bin/sh

GAME_USER="{args().user}" \\
IDLE_SERVER="{convert_bool_to_str(args().idle_time != 0)}" \\
IDLE_IF_TIME="{900 if args().idle_time == 0 else args().idle_time}" \\
SERVER_ROOT="$(pwd)" \\
BACKUP_DEST="$(pwd)/backup" \\
BACKUP_PATHS="{world_name} {world_name}_nether {world_name}_the_end" \\
KEEP_BACKUPS="{args().backups}" \\
SESSION_NAME="{args().name}" \\
GAME_PORT="{port}" \\
SERVER_START_CMD="{launch_command}" \\
fabricd $*
"""
		)
	
	# make the script executable
	os.chmod(fabric_env_file, os.stat(fabric_env_file).st_mode | stat.S_IEXEC)
