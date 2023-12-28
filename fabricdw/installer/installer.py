import json
import os
import shutil
import stat
import subprocess
from argparse import Namespace
from enum import StrEnum

import requests
from colorama import Fore, Style
from pick import pick

from fabricdw import convert_bool
from fabricdw.properties import modify_properties

SERVER_JAR_FILE: str = "fabric-server-launch.jar"
LAUNCH_COMMAND: str = "java -Dlog4j2.formatMsgNoLookups=true -Xms{min_ram}M -Xmx{max_ram}M -jar ./fabric-server-launch.jar nogui"
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


def print_installation_name(installation: dict, after: Fore = None) -> str:
	return print_installation_name_str(installation['name'], after=after)


def print_installation_name_str(installation_name: str, after: Fore = None) -> str:
	return f"{Fore.CYAN}{installation_name}{Style.RESET_ALL}{after if after else ''}"


def yes_no_question(question: str, yes_first: bool = False) -> bool:
	options = ["No", "Yes"]
	
	if yes_first:
		options = options[::-1]
	
	_, index = pick(options, question, indicator=">")
	
	return index == 1


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


def create_installation(active_installation: dict, args: Namespace) -> str | None:
	if active_installation is not None:
		print(f"{Fore.RED}installation '{print_installation_name(active_installation, after=Fore.RED)}' already exists! ({active_installation['root']}){Style.RESET_ALL}")
		return None
	
	os.makedirs(args.output_dir, exist_ok=True)
	active_dir: str = os.path.abspath(args.output_dir)
	
	try:
		return _create_installation(active_dir, args)
	except KeyboardInterrupt as kbe:
		print("Keyboard interrupt: Cleaning up...")
		remove_dir(active_dir)
		raise kbe


def _create_installation(active_dir: str, args: Namespace) -> str | None:
	if len(os.listdir(active_dir)) > 0 and not yes_no_question(f"The directory '{active_dir}' is not empty. Proceed anyway?"):
		print("cancelling installation")
		return None
	
	game_version, loader_version, installer_version = select_version()
	server_url = build_server_jar_url(game_version, loader_version, installer_version)
	
	server_jar = requests.get(server_url)
	
	jar_file = f"{active_dir}/{SERVER_JAR_FILE}"
	fabric_env_file = f"{active_dir}/{FABRIC_ENV_FILE}"
	
	with open(jar_file, "wb") as jar:
		jar.write(server_jar.content)
	
	print("initializing the server...")
	print(f"{Fore.RED}{Style.BRIGHT}This should not actually start the server!{Style.RESET_ALL}")
	subprocess.call(["java", "-jar", jar_file], cwd=active_dir, stdout=args.init_output)
	
	launch_command = LAUNCH_COMMAND.format(min_ram=int(args.min_ram * 1024), max_ram=int(args.max_ram * 1024))
	world_name = args.properties["level-name"]
	port = args.properties["server-port"]
	
	with open(fabric_env_file, 'w') as launch_script_file:
		launch_script_file.write(
			f"""#!/bin/sh
	GAME_USER="{args.user}" \\
	IDLE_SERVER="{convert_bool(args.idle_time != 0)}" \\
	IDLE_IF_TIME="{1200 if args.idle_time == 0 else args.idle_time}" \\
	SERVER_ROOT="{active_dir}" \\
	BACKUP_DEST="{active_dir}/backup" \\
	BACKUP_PATHS="{world_name} {world_name}_nether {world_name}_the_end" \\
	KEEP_BACKUPS="{args.backups}" \\
	SESSION_NAME="{args.name}" \\
	GAME_PORT="{port}" \\
	SERVER_START_CMD="{launch_command}" \\
	fabricd "$*"
	"""
		)
	
	# to run fabridw, it must be executable
	# give the EXEC flag to the file
	os.chmod(fabric_env_file, os.stat(fabric_env_file).st_mode | stat.S_IEXEC)
	
	modify_properties(active_dir, args.properties)
	
	print(f"installation '{print_installation_name_str(args.name)}' for {game_version['version']} created! ({active_dir})")
	
	return active_dir


def remove_installation(active_installation: dict, fallback_name: str) -> bool:
	if active_installation is None:
		print(f"{Fore.RED}installation '{print_installation_name_str(fallback_name, after=Fore.RED)}' does not exist!{Style.RESET_ALL}")
		return False
	
	if not os.path.exists(active_installation['root']) or not os.path.isdir(active_installation['root']):
		print(f"installation '{print_installation_name(active_installation)}' does not exist anymore.")
		return True
	elif yes_no_question(f"Remove installation '{active_installation['name']}' ({active_installation['root']})?\nThis will delete all files!"):
		remove_dir(active_installation['root'])
		print(f"installation '{print_installation_name(active_installation)}' ({active_installation['root']}) deleted!")
		return True
	
	print("nothing deleted")
	return False


def remove_dir(directory: str) -> None:
	shutil.rmtree(directory)
