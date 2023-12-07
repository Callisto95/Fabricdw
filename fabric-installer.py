#!/usr/bin/python

import json
import os.path
import os
import stat
import shutil
import requests
import subprocess
from argparse import ArgumentParser, Namespace
from colorama import Fore, Style
from enum import StrEnum
from pick import pick

CONFIG_FILE: str = os.path.expanduser("~/.config/fabricdw.json")

SERVER_JAR_FILE: str = "fabric-server-launch.jar"
LAUNCH_COMMAND: str = "java -Dlog4j2.formatMsgNoLookups=true -Xms{min_ram}M -Xmx{max_ram}M -jar ./fabric-server-launch.jar nogui"
FABRIC_ENV_FILE: str = "fabricdw"

API_URL: str = "https://meta.fabricmc.net/v2"
BASE_URL: str = f"{API_URL}/versions"


def print_installation_name(installation: dict, after: Fore = None) -> str:
	return f"{Fore.CYAN}{installation['name']}{Style.RESET_ALL}{after if after else ''}"


def print_installation_name_str(installation_name: str) -> str:
	return f"{Fore.CYAN}{installation_name}{Style.RESET_ALL}"


def remove_installation_from_list(config: dict, installation: dict) -> list[dict]:
	return [inst for inst in config['installations'] if inst['name'] != installation['name']]


def yes_no_question(question: str, yes_first: bool = False) -> bool:
	options = ["No", "Yes"]
	
	if yes_first:
		options = options[::-1]
	
	_, index = pick(options, question, indicator=">")
	
	return index == 1


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


def parse_args(config: dict) -> Namespace:
	parser = ArgumentParser()
	
	parser.add_argument("name", action="store")
	parser.add_argument("-d", "--directory", dest="output_dir", action="store", default=".")
	
	parser.add_argument("-r", "--remove", dest="remove", action="store_true")
	
	parser.add_argument("-mn", "--min-ram", dest="min_ram", action="store", type=float, default=config['default_min_ram'])
	parser.add_argument("-mx", "--max-ram", dest="max_ram", action="store", type=float, default=config['default_max_ram'])
	parser.add_argument("-p", "--port", dest="port", action="store", type=int, default=25565)
	
	parser.add_argument("-a", "--autoinit", dest="autoinit", action="store_true")
	parser.add_argument("--show-init-output", dest="init_output", action="store_const", default=subprocess.DEVNULL, const=None)
	
	args: Namespace = parser.parse_args()
	return args


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


def create_installation(active_installation: dict, active_dir: str, args: Namespace) -> bool:
	if active_installation is not None:
		print(f"{Fore.RED}installation '{print_installation_name(active_installation, after=Fore.RED)}' already exists! ({active_installation['root']}){Style.RESET_ALL}")
		return False
	
	if len(os.listdir(active_dir)) > 0 and not yes_no_question(f"The directory '{active_dir}' is not empty. Proceed anyway?"):
		print("cancelling installation")
		return False
	
	game_version, loader_version, installer_version = select_version()
	server_url = build_server_jar_url(game_version, loader_version, installer_version)
	
	server_jar = requests.get(server_url)
	
	jar_file = f"{active_dir}/{SERVER_JAR_FILE}"
	fabric_env_file = f"{active_dir}/{FABRIC_ENV_FILE}"
	
	with open(jar_file, "wb") as jar:
		jar.write(server_jar.content)
	
	if args.autoinit:
		print("initializing the server...")
		print(f"{Fore.RED}{Style.BRIGHT}This should not actually start the server!{Style.RESET_ALL}")
		subprocess.call(["java", "-jar", jar_file], cwd=active_dir, stdout=args.init_output)
	
	launch_command = LAUNCH_COMMAND.format(min_ram=int(args.min_ram*1024), max_ram=int(args.max_ram*1024))
	backup_dir = f"{active_dir}/backup"
	
	with open(fabric_env_file, 'w') as launch_script_file:
		launch_script_file.write(
			f"""#!/bin/sh
SERVER_ROOT=\"{active_dir}\" \\
BACKUP_DEST=\"{backup_dir}\" \\
SESSION_NAME=\"{args.name}\" \\
GAME_PORT=\"{args.port}\" \\
SERVER_START_CMD=\"{launch_command}\" \\
fabricd $*
"""
		)
		
		# to run fabridw, it must be executable
		# give the flag to the file
		os.chmod(fabric_env_file, os.stat(fabric_env_file).st_mode | stat.S_IEXEC)
		
		return True


def remove_installation(active_installation: dict, fallback_name: str) -> bool:
	if active_installation is None:
		print(f"{Fore.RED}installation '{print_installation_name_str(fallback_name)}' does not exist!{Style.RESET_ALL}")
		return False
	
	if not os.path.exists(active_installation['root']) or not os.path.isdir(active_installation['root']):
		print(f"installation '{print_installation_name(active_installation)}' does not exist anymore.")
		return True
	elif yes_no_question(f"Remove installation '{active_installation['name']}' ({active_installation['root']})?\nThis will delete all files!"):
		shutil.rmtree(active_installation['root'])
		return True
	
	print("nothing deleted")
	return False


def main() -> None:
	if os.path.exists(CONFIG_FILE):
		with open(CONFIG_FILE, 'r') as cfg:
			config = json.load(cfg)
	else:
		config = {
			'default_min_ram': 0.5,
			'default_max_ram': 6,
			'installations': []
		}
	
	args = parse_args(config)
	
	os.makedirs(args.output_dir, exist_ok=True)
	active_dir: str = os.path.abspath(args.output_dir)
	
	active_installation = None
	
	for installation in config['installations']:
		if args.name == installation['name']:
			active_installation = installation
			break
	
	if args.remove:
		if remove_installation(active_installation, args.name):
			config['installations'] = remove_installation_from_list(config, active_installation)
	else:
		if create_installation(active_installation, active_dir, args):
			config['installations'].append({
				'root': active_dir,
				'name': args.name
			})
	
	with open(CONFIG_FILE, 'w') as cfg:
		json.dump(config, cfg, indent=4)


if __name__ == "__main__":
	main()
