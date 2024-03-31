import json
import os
import shutil
import stat
import subprocess
from argparse import Namespace
from enum import StrEnum
from os.path import exists

import requests
from colorama import Fore, Style
from pick import pick

from fabricdw import convert_bool
from fabricdw.common import Installation, CONFIG, remove_dir, absolute_path, okay_to_write_into, yes_no_question
from fabricdw.common.properties import Properties, Defaults
from fabricdw.properties import modify_properties
from fabricdw.properties.modify import get_properties

SERVER_JAR_FILE: str = "fabric-server-launch.jar"
LAUNCH_COMMAND: str = "{java_executable}{java_args} -Dlog4j2.formatMsgNoLookups=true -Xms{min_ram}M -Xmx{max_ram}M -jar ./fabric-server-launch.jar nogui"
FABRIC_ENV_FILE: str = "fabricdw"

API_URL: str = "https://meta.fabricmc.net/v2"
BASE_URL: str = f"{API_URL}/versions"


# no enum for bool, class used instead
class VersionStability:
	STABLE: bool = True
	UNSTABLE: bool = False


class ApiUrls(StrEnum):
	GAME: str = f"{BASE_URL}/game"
	LOADER: str = f"{BASE_URL}/loader"
	INSTALLER: str = f"{BASE_URL}/installer"


def filter_versions(versions: list[dict], type: bool) -> list[dict]:
	filtered_versions = [version for version in versions if version['stable'] is type]
	
	return filtered_versions


def get_versions(type: ApiUrls) -> list[dict]:
	versions = json.loads(requests.get(type).text)
	
	return versions


def build_server_jar_url(game, loader, installer) -> str:
	return f"{BASE_URL}/loader/{game['version']}/{loader['version']}/{installer['version']}/server/jar"


def custom_version_selection(game_versions: list[dict], loader_versions: list[dict], installer_versions: list[dict]) -> tuple[dict, dict, dict]:
	# option is quite different from what is needed
	_, game_index = pick([game['version'] for game in game_versions], "select game version", indicator=">")
	_, loader_index = pick([loader['version'] for loader in loader_versions], "select loader version", indicator=">")
	_, installer_index = pick([installer['version'] for installer in installer_versions], "select installer version", indicator=">")
	
	return game_versions[game_index], loader_versions[loader_index], installer_versions[installer_index]


def select_version() -> tuple[dict, dict, dict]:
	print("getting latest versions...")
	
	game_versions = get_versions(ApiUrls.GAME)
	loader_versions = get_versions(ApiUrls.LOADER)
	installer_versions = get_versions(ApiUrls.INSTALLER)
	
	stable_game_versions = filter_versions(game_versions, VersionStability.STABLE)
	stable_loader_versions = filter_versions(loader_versions, VersionStability.STABLE)
	stable_installer_versions = filter_versions(installer_versions, VersionStability.STABLE)
	
	unstable_game_versions = filter_versions(game_versions, VersionStability.UNSTABLE)
	
	# loader and installer are latest by default
	# any 'unstable' loader or installer are out of date
	latest_stable = stable_game_versions[0]['version']
	latest_unstable = unstable_game_versions[0]['version']
	
	_, index = pick([
		f"latest ({latest_stable})",
		f"latest-unstable ({latest_unstable})",
		"custom"
	], "select version", indicator=">")
	
	match index:
		case 0:
			return stable_game_versions[0], stable_loader_versions[0], stable_installer_versions[0]
		case 1:
			return unstable_game_versions[0], stable_loader_versions[0], stable_installer_versions[0]
		case 2 | _:  # default case so that mypy is pleased
			return custom_version_selection(game_versions, loader_versions, installer_versions)


def set_property_if_not_defined(args: Namespace, prop_name: str, fallback: str) -> None:
	if prop_name not in args.properties:
		args.properties[prop_name] = fallback


def create_installation(args: Namespace) -> None:
	active_installation: Installation = CONFIG.get_installation(args.name)
	
	if active_installation is not None:
		print(f"{Fore.RED}installation '{active_installation.pretty_name(Fore.RED)}' already exists! ({active_installation.root}){Style.RESET_ALL}")
		return
	
	os.makedirs(args.output_dir, exist_ok=True)
	active_dir: str = absolute_path(args.output_dir)
	
	# required by the installer
	set_property_if_not_defined(args, Properties.WORLD_NAME, Defaults.WORLD_NAME)
	set_property_if_not_defined(args, Properties.PORT_SERVER, Defaults.PORT_SERVER)
	
	try:
		_dir = _create_installation(active_dir, args)
		
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


def _create_installation(active_dir: str, args: Namespace, init_server: bool = True, filled_ok: bool = False) -> str | None:
	if not filled_ok and not okay_to_write_into:
		return None
	
	fabric_env_file = f"{active_dir}/{FABRIC_ENV_FILE}"
	
	if init_server:
		game_version, loader_version, installer_version = select_version()
		server_url = build_server_jar_url(game_version, loader_version, installer_version)
		
		server_jar = requests.get(server_url)
		
		jar_file = f"{active_dir}/{SERVER_JAR_FILE}"
		
		with open(jar_file, "wb") as jar:
			jar.write(server_jar.content)
		
		print("initializing the server...")
		print(f"{Fore.RED}{Style.BRIGHT}This should not actually start the server!{Style.RESET_ALL}")
		subprocess.call(["java", "-jar", jar_file], cwd=active_dir, stdout=args.init_output)
	
	launch_command = LAUNCH_COMMAND.format(java_executable=args.java_executable, java_args=format_java_args(args.java_args), min_ram=int(args.min_ram * 1024), max_ram=int(args.max_ram * 1024))
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
	
	modify_properties(active_dir, args.properties)
	
	return active_dir
