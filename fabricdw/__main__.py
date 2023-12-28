import getpass
import json
import os
import os.path
import subprocess
from argparse import ArgumentParser, Namespace
from typing import Any

from fabricdw.installer import remove_installation
from fabricdw.installer.installer import create_installation
from fabricdw.properties import create_replacements

CONFIG_FILE: str = os.path.expanduser("~/.config/fabricdw.json")


def set_if_not_defined(args: Namespace, prop_name: str, fallback: Any) -> None:
	if prop_name not in args.properties:
		args.properties[prop_name] = fallback


def parse_args(defaults: dict) -> Namespace:
	parser = ArgumentParser()
	
	parser.add_argument("name", action="store", type=str, help="name of the installation")
	
	parser.add_argument("-d", "--directory", action="store", type=str, dest="output_dir", default=None)
	parser.add_argument("-r", "--remove", action="store_true", dest="remove")
	parser.add_argument("-u", "--user", action="store", type=str, dest="user", default=getpass.getuser())
	
	parser.add_argument("-mn", "--min-ram", action="store", type=float, dest="min_ram", default=defaults['min_ram'])
	parser.add_argument("-mx", "--max-ram", action="store", type=float, dest="max_ram", default=defaults['max_ram'])
	
	parser.add_argument("-p", "--port", action="store", type=int, dest="port", default=25565)
	parser.add_argument("-b", "--backups", action="store", type=int, dest="backups", default=defaults['backups'])
	parser.add_argument("-i", "--idle-time", action="store", type=int, dest="idle_time", default=defaults['idle_time'])
	
	parser.add_argument("--show-init-output", action="store_const", dest="init_output", default=subprocess.DEVNULL, const=None)
	
	parser.add_argument("-property", action="append", type=str, dest="properties", default=[])
	
	args: Namespace = parser.parse_args()
	
	args.properties = create_replacements(args)
	
	# required by the installer
	set_if_not_defined(args, "level-name", "world")
	set_if_not_defined(args, "server-port", 25565)
	
	# query port should be server port, if not set explicitly
	if args.properties["server-port"] != 25565 and "query.port" not in args.properties:
		args.properties["query.port"] = args.properties["server-port"]
	
	# do not use the current dir
	if args.output_dir is None:
		args.output_dir = f"./{args.name}"
	
	return args


def main() -> None:
	if os.path.exists(CONFIG_FILE):
		with open(CONFIG_FILE, 'r') as cfg:
			config = json.load(cfg)
	else:
		print("config file missing, creating new")
		config = {
			"defaults": {
				"min_ram": 0.5,
				"max_ram": 6,
				"idle_time": 0,
				"backups": 5,
			},
			'installations': []
		}
	
	args = parse_args(config['defaults'])
	
	active_installation: dict | None = None
	
	for installation in config['installations']:
		if args.name == installation['name']:
			active_installation = installation
			break
	
	if args.remove:
		if remove_installation(active_installation, args.name):
			config['installations'] = [inst for inst in config['installations'] if inst['name'] != active_installation['name']]
	else:
		_dir = create_installation(active_installation, args)
		
		if _dir:
			config['installations'].append({
				'root': _dir,
				'name': args.name
			})
	
	with open(CONFIG_FILE, 'w') as cfg:
		json.dump(config, cfg, indent=4)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Keyboard interrupt! Exiting!")
