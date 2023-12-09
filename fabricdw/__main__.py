import getpass
import json
import os.path
import os
import subprocess
from argparse import ArgumentParser, Namespace

from fabricdw.installer import remove_installation
from fabricdw.installer.installer import create_installation

CONFIG_FILE: str = os.path.expanduser("~/.config/fabricdw.json")


def parse_args(defaults: dict) -> Namespace:
	parser = ArgumentParser()
	
	parser.add_argument("name", action="store", type=str, help="name of the installation")
	
	parser.add_argument("-d", "--directory", action="store", type=str, dest="output_dir", default=".")
	parser.add_argument("-r", "--remove", action="store_true", dest="remove")
	parser.add_argument("-u", "--user", action="store", type=str, dest="user", default=getpass.getuser())
	
	parser.add_argument("-mn", "--min-ram", action="store", type=float, dest="min_ram", default=defaults['min_ram'])
	parser.add_argument("-mx", "--max-ram", action="store", type=float, dest="max_ram", default=defaults['max_ram'])
	
	parser.add_argument("-p", "--port", action="store", type=int, dest="port", default=25565)
	parser.add_argument("-b", "--backups", action="store", type=int, dest="backups", default=defaults['backups'])
	parser.add_argument("-i", "--idle-time", action="store", type=int, dest="idle_time", default=defaults['idle_time'])
	
	parser.add_argument("--show-init-output", action="store_const", dest="init_output", default=subprocess.DEVNULL, const=None)
	
	parser.add_argument("-w", "--world-name", action="store", type=str, dest="world_name", default="world")
	parser.add_argument("-s", "--seed", action="store", type=int, dest="seed", default=None)
	parser.add_argument("-df", "--difficulty", action="store", type=str, dest="difficulty", default=defaults['difficulty'], choices=["peaceful", "easy", "normal", "hard"])
	parser.add_argument("-gm", "--gamemode", action="store", type=str, dest="game_mode", default=defaults['gamemode'], choices=["survival", "adventure", "creative", "spectator"])
	
	args: Namespace = parser.parse_args()
	
	if args.seed is None:
		args.seed = ""
	
	return args


def main() -> None:
	if os.path.exists(CONFIG_FILE):
		with open(CONFIG_FILE, 'r') as cfg:
			config = json.load(cfg)
	else:
		config = {
			"defaults": {
				"min_ram": 0.5,
				"max_ram": 6,
				"idle_time": 0,
				"gamemode": "survival",
				"difficulty": "normal",
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
	main()
